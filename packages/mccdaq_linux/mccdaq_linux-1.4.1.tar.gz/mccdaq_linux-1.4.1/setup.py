from distutils.core import setup, Extension
from Cython.Distutils import build_ext
import numpy
import sys

sys.path.append('/media/labdata/Brillouin/Python/utilities')

print sys.path

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: C',
    'Programming Language :: Cython',
    'Programming Language :: Python :: 2.7',
    'Topic :: Home Automation',
    'Topic :: Scientific/Engineering'
]

usb2600_wrapper = Extension("usb2600.wrapper",
		   #sources = ["mccdaq/usb2600/usb2600.pyx", "mccdaq/usb2600/mccdaq-extra.c"],
		   sources = ["usb2600/usb2600.pyx", "usb2600/mccdaq-extra.c"],
		   library_dirs = ['.','usr/local/lib'],
		   include_dirs = ['usb2600', '.', '..', numpy.get_include(),'/usr/lib64/python/site-packages/Cython/Includes', 'mcc-libhid'],
		   libraries = ['usb', 'hid', 'mcchid', 'm', 'c'])


setup(
    name = 'mccdaq_linux',
    version = '1.4.1',
    description = "Python drivers for Measurement Computing devices (mccdaq.com) on linux",
    author = 'Guillaume Lepert',
    author_email = 'guillaume.lepert07@imperial.ac.uk',
    long_description="""Python drivers for data acquisition hardware from Measurement Computing (http://mccdaq.com/).

    Currently only USB26xx devices are supported, but we could add more.
    
    Complete support for timers, counters, single-sample digital and analog input/output,
    waveform generation, synchronous analog input/output scanning, external/internal triggering;
    in a user-friendly, interactive, object-oriented format.
    """,
    packages=['usb2600'],
    cmdclass={'build_ext': build_ext},
    ext_modules = [usb2600_wrapper],
    #py_modules = ['mccdaq/usb2600/usb2600', 'mccdaq/waveform'],
    py_modules = ['usb2600/usb2600', '/media/labdata/Brillouin/Python/utilities/waveform/waveform','__init__'],
    data_files = ['usb2600/usb2600.pxd'],
        #requires=['waveform'],
    platforms=['linux'],
    classifiers = classifiers
    
)

#A Python driver for MCCDAQ's USB2600 data acquisition devices, providing: 

    #- a Cython wrapper to Warren Jasper's original Linux MCCDAQ driver (available here_),

    #- an object-oriented interface build on top of the Cython wrapper.

    #The driver includes advanced functionalities for analog input and output scans of arbitrary length and synchronous analog input/output scanning.

    #Get in touch if anybody is interested in adding support for other MCC devices.

    #.. _here: ftp://lx10.tx.ncsu.edu/pub/Linux/drivers/USB
    #""",
