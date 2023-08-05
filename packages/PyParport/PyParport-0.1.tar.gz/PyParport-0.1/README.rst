=========
PyParport
=========
(Version 0.0.1)

*******
Purpose
*******
Connect to the first parallel port from Python.

Usage
=====
You need to import PyParport. This function provides a read() and a write() method. Both take the needed register as argument: d(ata), c(ontrol) or s(tatus). The write method also take the value to write as decimal number.

For example:
************
import PyParport

# To show the data of the data register
PyParport.read("d")

# To show the data of the control register
PyParport.read("c")

# To show the data of the status register
PyParport.read("s")

# To write a 0 to the data register
PyPaport.write(0, "d")

# To write a 255 to the data register
PyPaport.write(255, "d")


License
=======
PyParport is avialable under the terms of the GPLv3.


Disclaimer
==========
This software comes without any warranty. You use it on your own risk. It may contain bugs, viruses or harm your hardware in another way. The developer is not responsible for any consequences which may occur because of using the software.
