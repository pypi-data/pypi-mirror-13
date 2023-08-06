from setuptools import setup

setup(
        name='suspect',
        version='0.0.4',
        packages=['suspect', 'tests'],
        url='https://github.com/bennyrowland/suspect.git',
        license='MIT',
        author='bennyrowland',
        author_email='bennyrowland@mac.com',
        description='',
        entry_points={
        },
        classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 2 - Pre-Alpha',

            # Indicate who your project is intended for
            'Intended Audience :: Science/Research',
            'Topic :: Scientific/Engineering :: Medical Science Apps.',
            'Topic :: Scientific/Engineering :: Physics',

            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: MIT License',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
        ],
        install_requires=['numpy', 'pytest', 'mock']
)
