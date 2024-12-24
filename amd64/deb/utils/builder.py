#!/usr/bin/env python3

import yaml
import utils.cxx
import utils.boot

class Builder :

    def __init__ (self, config):
        with open(config, 'r') as file :
            self._cfg = yaml.safe_load (file)
            self._gcc_version = self._cfg ["gcc_version"]
            self._versions = self._cfg ["ymir_versions"]


    def run (self):
        for v in self._versions:
            if v == "cxx_version":
                utils.cxx.CxxBuilder (self._gcc_version).run ()
            elif v == "bootstrap_v0.1" :
                utils.boot.BootstrapBuilder ("v0.1").run ()
