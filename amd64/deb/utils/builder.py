#!/usr/bin/env python3

import yaml
import requests
import os

import utils.cxx
import utils.gyllir
import utils.bootstrap

class Builder:
    
    def __init__ (self, config):
        with open(config, 'r') as file :
            self._cfg = yaml.safe_load (file)
            self._versions = self._cfg ["ymir_versions"]


    def run (self):
        try:
            os.mkdir(f"results")
            print(f"Directory '{directory_name}' created successfully.")
        except Exception:
            pass

        for v in self._versions:
            if v == "cxx_version":
                # target gcc-13.2.0, compiled with gcc-13.2.0
                utils.cxx.CxxBuilder ("13.2.0", "13.2.0").run ()
                utils.gyllir.GyllirBuilder ("13.2.0", "cxx").run ()
            elif v == "bootstrap_v0.1":
                # target gcc-13.2.0, compiled with gcc-13.2.0
                utils.bootstrap.VxxBuilder ("13.2.0", "13.2.0", "13.2.0", "cxx", "0.1.0").run ()
                utils.gyllir.GyllirBuilder ("13.2.0", "0.1.0").run ()
            elif v == "bootstrap_v1.0":
                # target gcc-13.2.0, compiled with gcc-13.2.0
                utils.bootstrap.VxxBuilder ("13.2.0", "13.2.0", "13.2.0", "0.1.0", "1.0.0").run ()
                utils.gyllir.GyllirBuilder ("13.2.0", "1.0.0").run ()
            elif v == "bootstrap_v1.1":
                # target gcc-15.2.0, but still compiled with gcc-13.2.0
                utils.bootstrap.VxxBuilder ("15.2.0", "13.2.0", "13.2.0", "1.0.0", "1.1.0").run ()
                utils.gyllir.GyllirBuilder ("15.2.0", "1.1.0").run ()
            elif v == "bootstrap_v1.2":
                # target gcc-15.2.0, compiled with gcc-15.2.0
                utils.bootstrap.VxxBuilder ("15.2.0", "15.2.0", "15.2.0", "1.1.0", "1.2.0").run ()
                #utils.gyllir.GyllirBuilder ("15.2.0", "1.2.0").run ()

            else:
                print (f"Version {v} unknown")
                print ("Available versions are :")
                print ("- 'cxx_version'")
                print ("- 'bootstrap_v0.1' (depends on version_cxx)")
                print ("- 'bootstrap_v1.0' (depends on v0.1)")
                print ("- 'bootstrap_v1.1' (depends on v1.0)")
                print ("- 'bootstrap_v1.1_alone' (depends on v1.1 or v1.1_alone)")
