#!/usr/bin/env python
#! coding: utf-8

import _interface


class Port(object):
    """ Abstraction layer for a more comfortable use """

    def __init__(self, port):
        self.port = port

    def read(self):
        return _interface.read(self.port)

    def write(self, value):
        return _interface.write(value, self.port)


class PyParport(object):
    """ The main class which implements the interface to the port """
    data = Port("d")
    control = Port("c")
    status = Port("s")

    # The register addressess are here just for later implementation
    # data_address = 0x378
    # status_address = 0x379
    # control_address = 0x37A
