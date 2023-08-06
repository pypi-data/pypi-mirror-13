=========
PyParport
=========
(Version 0.5)

*******
Purpose
*******
Connect to a parallel port from Python.


Usage
=====
Instances of the PyParport class provide a data, a status and a control method. Each method has a read() and a write() method. The write method take the value to write as an integer as argument.


Example:
********

.. code:: python

    from pyparport import PyParport
    port = PyParport()

    # To show the data of the data register:
    port.data.read()

    # To write a 255 to the data register:
    port.data.write(255)

According to the registers of the parallel port, the PyParport class implements the following methods:

- data

- control

- status

You can change the base address of the port on object initialisation:

.. code:: python

    port = PyParport(base_address=632)


License
=======
PyParport is available under the terms of the GPLv3.


Disclaimer
==========
This software comes without any warranty. You use it on your own risk. It may contain bugs, viruses or harm your hardware in another way. The developer is not responsible for any consequences which may occur because of using the software.
