#!/usr/bin/env python3

class BootstrapBuilder:
    def __init__ (self, version):
        self._version = version

    def run (self) :
        print ("Building Bootstrap version : ", self._version)
