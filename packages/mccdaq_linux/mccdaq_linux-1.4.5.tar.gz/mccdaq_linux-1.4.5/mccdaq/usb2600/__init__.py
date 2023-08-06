# mccdaq/usb2600/.__init__.py
"""Linux driver for MCCDAQ USB-26xx devices.

.. seealso::

   - `Website <http://www.mccdaq.com/usb-data-acquisition/USB-2627.aspx>`_
   
   - `User's guide <../../../../../../Datasheets/MCCDAQ/MCC_USB-2627 DAQ.pdf>`_
   
   - `Specifications <../../../../../../Datasheets/MCCDAQ/USB-2600-Series-data.pdf>`_

   - `Warren Jasper's C driver <ftp://lx10.tx.ncsu.edu/pub/Linux/drivers/USB/>`_

.. toctree::
   :maxdepth: 2

   usb2600.usb2600
   usb2600.wrapper

.. Note::
   To build the usb2600.wrapper extension, do::
     
     $ cd mccdaq/usb2600/
     $ python2.7 setup_extension.py build_ext --inplace

"""

#__import__('pkg_resources').declare_namespace(__name__)

from usb2600 import USB2600
from wrapper import USB2600_Wrapper
