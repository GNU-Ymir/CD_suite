#!/usr/bin/env python3

import yaml
import requests
import os

import utils.cxx
import utils.gyllir
import utils.bootstrap
from utils.versions import GycVersions

class Builder:

    def __init__ (self, config):
        with open(config, 'r') as file :
            self._cfg = yaml.safe_load (file)
            self._versions = self._cfg ["ymir_versions"]


    def run (self):
        try:
            os.mkdir(f"results")
        except Exception:
            pass

        # Ubuntu base image is picked per GCC major: 13.x needs ubuntu 24.04 (ubuntu 26.04's
        # libs are too new to build/run gcc-13 against), 15.x uses ubuntu 26.04.
        UBUNTU_FOR_GCC13 = "24.04"
        UBUNTU_FOR_GCC15 = "26.04"

        for v in self._versions:
            if v == "cxx_version":
                # target gcc-13, compiled with gcc-13, both on ubuntu 24.04
                utils.cxx.CxxBuilder ("13", "13", UBUNTU_FOR_GCC13).run ()
                utils.gyllir.GyllirBuilder (gyc="13_cxx", compile_with="13", gyllir_version="cxx", ubuntu_version=UBUNTU_FOR_GCC13).run ()
            elif v == "bootstrap_v0.1":
                # target gcc-13, compiled with gcc-13, both on ubuntu 24.04
                utils.bootstrap.VxxBuilder (
                    prev_gyc="13_cxx",
                    prev_gyllir="cxx",
                    versions=GycVersions (compiler="13", target="13", ymir="0.1.0", bootstrap="0.1.0", midgard="0.1.0"),
                    ubuntu_version=UBUNTU_FOR_GCC13,
                ).run ()
                utils.gyllir.GyllirBuilder (gyc="13_0.1.0", compile_with="13", gyllir_version="0.1.0", ubuntu_version=UBUNTU_FOR_GCC13).run ()
            elif v == "bootstrap_v1.0":
                # target gcc-13, compiled with gcc-13, both on ubuntu 24.04
                utils.bootstrap.VxxBuilder (
                    prev_gyc="13_0.1.0",
                    prev_gyllir="0.1.0",
                    versions=GycVersions (compiler="13", target="13", ymir="1.0.0", bootstrap="1.0.0", midgard="1.0.0"),
                    ubuntu_version=UBUNTU_FOR_GCC13,
                ).run ()
                utils.gyllir.GyllirBuilder (gyc="13_1.0.0", compile_with="13", gyllir_version="1.0.0", ubuntu_version=UBUNTU_FOR_GCC13).run ()
            elif v == "bootstrap_v1.1":
                # target gcc-15, but still compiled with gcc-13 (single ubuntu axis picks the
                # compiler's ubuntu here, since that's what fetch_gcc_version/configure/make need)
                utils.bootstrap.VxxBuilder (
                    prev_gyc="13_1.0.0",
                    prev_gyllir="1.0.0",
                    versions=GycVersions (compiler="13", target="15", ymir="1.1.0", bootstrap="1.1.0", midgard="1.1.0"),
                    ubuntu_version=UBUNTU_FOR_GCC13,
                ).run ()
                # install_gyc here installs the just-built gcc-15-targeted deb, so it needs the
                # target's ubuntu (26.04), not the compiler's (24.04) used to build it above.
                utils.gyllir.GyllirBuilder (gyc="15_1.1.0", compile_with="15", gyllir_version="1.1.0", ubuntu_version=UBUNTU_FOR_GCC15).run ()
            elif v == "bootstrap_v1.1.1":
                # target gcc-15, compiled with gcc-15, both on ubuntu 26.04
                utils.bootstrap.VxxBuilder (
                    prev_gyc="15_1.1.0",
                    prev_gyllir="1.1.0",
                    versions=GycVersions (compiler="15", target="15", ymir="1.1.1", bootstrap="1.1.1", midgard="1.1.1"),
                    ubuntu_version=UBUNTU_FOR_GCC15,
                ).run ()
                utils.gyllir.GyllirBuilder (gyc="15_1.1.1", compile_with="15", gyllir_version="1.1.1", ubuntu_version=UBUNTU_FOR_GCC15).run ()
            elif v == "bootstrap_v1.2":
                # target gcc-15, compiled with gcc-15, both on ubuntu 26.04
                utils.bootstrap.VxxBuilder (
                    prev_gyc="15_1.1.1",
                    prev_gyllir="1.1.1",
                    versions=GycVersions (compiler="15", target="15", ymir="1.2.0", bootstrap="1.2.0", midgard="1.2.0"),
                    ubuntu_version=UBUNTU_FOR_GCC15,
                ).run ()
                #utils.gyllir.GyllirBuilder (gyc="15_1.2.0", compile_with="15", gyllir_version="1.2.0", ubuntu_version=UBUNTU_FOR_GCC15).run ()

            else:
                print (f"Version {v} unknown")
                print ("Available versions are :")
                print ("- 'cxx_version'")
                print ("- 'bootstrap_v0.1' (depends on version_cxx)")
                print ("- 'bootstrap_v1.0' (depends on v0.1)")
                print ("- 'bootstrap_v1.1' (depends on v1.0)")
                print ("- 'bootstrap_v1.1.1' (depends on v1.1)")
                print ("- 'bootstrap_v1.2' (depends on v1.1.1)")
