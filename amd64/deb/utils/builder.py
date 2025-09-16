#!/usr/bin/env python3

import yaml
import utils.cxx
import utils.boot
import utils.gyllir


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
                utils.gyllir.GyllirBuilder (self._gcc_version, "cxx").run ()
            elif v == "bootstrap_v0.1" :
                utils.boot.BootstrapBuilder (self._gcc_version, "cxx", "v0.1").run ()
                utils.gyllir.GyllirBuilder (self._gcc_version, "v0.1").run ()
            elif v == "bootstrap_v1.0":
                utils.boot.BootstrapBuilder (self._gcc_version, "v0.1", "v1.0").run ()
                utils.gyllir.GyllirBuilder (self._gcc_version, "v1.0").run ()
            elif v == "bootstrap_v1.1":
                utils.boot.BootstrapBuilder (self._gcc_version, "v1.0", "v1.1").run ()
                utils.gyllir.GyllirBuilder (self._gcc_version, "v1.1").run ()
            elif v == "bootstrap_v1.1_alone":
                utils.boot.BootstrapBuilder (self._gcc_version, "v1.1", "v1.1").run ()
                utils.gyllir.GyllirBuilder (self._gcc_version, "v1.1").run ()
            else:
                print (f"Version {v} unknown")
                print ("Available versions are :")
                print ("- 'cxx_version'")
                print ("- 'bootstrap_v0.1' (depends on version_cxx)")
                print ("- 'bootstrap_v1.0' (depends on v0.1)")
                print ("- 'bootstrap_v1.1' (depends on v1.0)")
                print ("- 'bootstrap_v1.1_alone' (depends on v1.1 or v1.1_alone)")
