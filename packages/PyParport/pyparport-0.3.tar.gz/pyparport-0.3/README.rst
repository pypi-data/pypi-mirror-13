=========
PyParport
=========
(Version 0.2)

*******
Purpose
*******
Connect to the first parallel port from Python.

Usage
=====
You need to import PyParport. This function provides a read() and a write() method. Both take the needed register as argument: d(ata), c(ontrol) or s(tatus). The write method also take the value to write as decimal number.

Example:
********
.. code:: python

    from pyparport import PyParport

    # To show the data of the data register:
    PyParport.data.read()

    # To write a 255 to the data register:
    PyPaport.data.write(255)

PyParport class implements the following registers:
- data
- control
- status

Each register brings a read and a write method.

License
=======
PyParport is available under the terms of the GPLv3.


Disclaimer
==========
This software comes without any warranty. You use it on your own risk. It may contain bugs, viruses or harm your hardware in another way. The developer is not responsible for any consequences which may occur because of using the software.
