from suspect import MRSData

import struct
import numpy
import re

# This file largely relies on information from Siemens regarding the structure
# of the TWIX file formats. Most of the parameters that are read use the same
# names as those apparently used internally at Siemens. The purpose of some of
# these parameters is not currently clear but we break them out anyway.


class TwixBuilder(object):
    def __init__(self):
        self.header_params = None
        self.dt = None
        self.np = None
        self.num_channels = None
        self.data = []
        self.loop_counters = []

    def set_header_string(self, header_string):
        self.header_params = parse_twix_header(header_string)

    def set_np(self, np):
        if self.np is None:
            self.np = np
        else:
            if self.np != np:
                raise ValueError("TwixBuilder already has an np of {}, now trying to set a different value of {}".format(self.np, np))

    def set_num_channels(self, num_channels):
        if self.num_channels is None:
            self.num_channels = num_channels
        else:
            if self.num_channels != num_channels:
                raise ValueError("TwixBuilder num_channels already set to {}, now being changed to {}".format(self.num_channels, num_channels))

    def add_scan(self, loop_counters, scan_data):
        self.loop_counters.append(loop_counters)
        self.data.append(scan_data)

    def build_mrsdata(self):
        loop_counter_array = numpy.array(self.loop_counters)
        data_shape = 1 + numpy.max(loop_counter_array, axis=0) - numpy.min(loop_counter_array, axis=0)
        data_shape = numpy.append(data_shape, (self.num_channels, self.np))
        data = numpy.zeros(data_shape, dtype='complex')
        for i, loop_counter in enumerate(loop_counter_array):
            # have to break out the loop_counter parameters individually, the second line should work but doesn't
            data[loop_counter[0], loop_counter[1], loop_counter[2], loop_counter[3], loop_counter[4], loop_counter[5], loop_counter[6], loop_counter[7], loop_counter[8], loop_counter[9], loop_counter[10], loop_counter[11], loop_counter[12], loop_counter[13]] = self.data[i]
            #data[loop_counter] = self.data[i]

        # get rid of all the size 1 dimensions
        data = data.squeeze()

        mrs_data = MRSData(data, self.header_params["dt"], self.header_params["f0"])

        return mrs_data


def parse_twix_header(header_string):
    # get the name of the protocol being acquired
    protocol_name_string = re.search(r"<ParamString.\"tProtocolName\">  { \".+\"  }\n", header_string).group()
    protocol_name = protocol_name_string.split("\"")[3]
    # get information about the subject being scanned
    patient_id_string = re.search(r"<ParamString.\"PatientID\">  { \".+\"  }\n", header_string).group()
    patient_id = patient_id_string.split("\"")[3]
    # get the scan parameters
    frequency_string = re.search(r"<ParamLong.\"Frequency\">  { \d*  }", header_string).group()
    number_string = re.search(r"[0-9]+", frequency_string).group()
    frequency = int(number_string) * 1e-6
    frequency_string = re.search(r"<ParamLong.\"DwellTimeSig\">  { \d*  }", header_string).group()
    number_string = re.search(r"[0-9]+", frequency_string).group()
    dwell_time = int(number_string) * 1e-9
    return {"protocol_name": protocol_name,
            "patient_id": patient_id,
            "dt": dwell_time,
            "f0": frequency
            }


def load_twix_vb(fin, builder):

    # first four bytes are the size of the header
    header_size = struct.unpack("I", fin.read(4))[0]

    # read the rest of the header minus the four bytes we already read
    header = fin.read(header_size - 4)
    # for some reason the last 24 bytes of the header contain some junk that is not a string
    header = header[:-24].decode('windows-1252')
    builder.set_header_string(header)

    # the way that vb files are set up we just keep reading scans until the acq_end flag is set

    while True:

        # start by keeping track of where in the file this scan started
        # this will be used to jump to the start of the next scan
        start_position = fin.tell()

        # the first four bytes contain composite information
        temp = struct.unpack("I", fin.read(4))[0]

        # 25 LSBs contain DMA length (size of this scan)
        DMA_length = temp & (2 ** 26 - 1)
        # next we have the "pack" flag bit and the rest is PCI_rx
        # not sure what either of these are for but break them out in case
        pack_flag = (temp >> 25) & 1
        PCI_rx = temp >> 26

        meas_uid, scan_counter, time_stamp, pmu_time_stamp = struct.unpack("IIII", fin.read(16))

        # next long int is actually a lot of bit flags
        # a lot of them don't seem to be relevant for spectroscopy
        eval_info_mask = struct.unpack("Q", fin.read(8))[0]
        acq_end = eval_info_mask & 1
        rt_feedback = eval_info_mask >> 1 & 1
        hp_feedback = eval_info_mask >> 2 & 1
        sync_data = eval_info_mask >> 5 & 1
        raw_data_correction = eval_info_mask >> 10 & 1
        ref_phase_stab_scan = eval_info_mask >> 14 & 1
        phase_stab_scan = eval_info_mask >> 15 & 1
        sign_rev = eval_info_mask >> 17 & 1
        phase_correction = eval_info_mask >> 21 & 1
        pat_ref_scan = eval_info_mask >> 22 & 1
        pat_ref_ima_scan = eval_info_mask >> 23 & 1
        reflect = eval_info_mask >> 24 & 1
        noise_adj_scan = eval_info_mask >> 25 & 1

        if acq_end:
            break

        # if any of these flags are set then we should ignore the scan data
        if rt_feedback or hp_feedback or phase_correction or noise_adj_scan or sync_data:
            fin.seek(start_position + DMA_length)
            continue

        # now come the actual parameters of the scan
        num_samples, num_channels = struct.unpack("HH", fin.read(4))
        builder.set_num_channels(num_channels)

        # the loop counters are a set of 14 shorts which are used as indices
        # for the parameters an acquisition might loop over, including
        # averaging repetitions, COSY echo time increments and CSI phase
        # encoding steps
        # we have no prior knowledge about which counters might loop in a given
        # scan so we have to read in all scans and then sort out the data shape
        loop_counters = struct.unpack("14H", fin.read(28))

        cut_off_data, kspace_centre_column, coil_select, readout_offcentre = struct.unpack("IHHI", fin.read(12))
        time_since_rf, kspace_centre_line_num, kspace_centre_partition_num = struct.unpack("IHH", fin.read(8))

        ice_program_params = struct.unpack("4H", fin.read(8))
        free_params = struct.unpack("4H", fin.read(8))

        # there are some dummy points before the data starts
        num_dummy_points = free_params[0]

        # we want our np to be the largest power of two within the num_samples - num_dummy_points
        np = int(2 ** numpy.floor(numpy.log2(num_samples - num_dummy_points)))
        builder.set_np(np)

        slice_position = struct.unpack("7f", fin.read(28))

        # construct a numpy ndarray to hold the data from all the channels in this scan
        scan_data = numpy.zeros((num_channels, np), dtype='complex')

        # loop over all the channels and extract data
        for channel_index in range(num_channels):
            channel_id, ptab_pos_neg = struct.unpack("Hh", fin.read(4))
            raw_data = struct.unpack("<{}f".format(num_samples * 2), fin.read(num_samples * 4 * 2))
            # turn the raw data into complex pairs
            data_iter = iter(raw_data)
            complex_iter = (complex(r, -i) for r, i in zip(data_iter, data_iter))
            scan_data[channel_index, :] = numpy.fromiter(complex_iter, "complex64", num_samples)[num_dummy_points:(num_dummy_points + np)]

            # the vb format repeats all the header data for each channel in
            # turn, obviously this is redundant so we read all but the channel
            # index from the next header here
            fin.read(124)

        # pass the data from this scan to the builder
        builder.add_scan(loop_counters, scan_data)

        # go to the next scan and the top of the loop
        fin.seek(start_position + DMA_length)


def load_twix_vd(fin, builder):
    pass


def load_twix(filename):
    with open(filename, 'rb') as fin:

        # we can tell the type of file from the first two uints in the header
        first_uint, second_uint = struct.unpack("II", fin.read(8))

        # reset the file pointer before giving to specific function
        fin.seek(0)

        # create a TwixBuilder object for the actual loader function to use
        builder = TwixBuilder()

        if first_uint == 0 and second_uint <= 64:
            load_twix_vd(fin, builder)
        else:
            load_twix_vb(fin, builder)

    return builder.build_mrsdata()