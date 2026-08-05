#!/usr/bin/env python3

import yaml
import requests
import os

import utils.cxx
import utils.gyllir
import utils.bootstrap
from utils.versions import STAGES, CxxStage, BootstrapStage

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

        for v in self._versions:
            stage = STAGES.get (v)
            if stage is None:
                print (f"Version {v} unknown")
                print ("Available versions are :")
                for name in STAGES:
                    print (f"- '{name}'")
                continue

            if isinstance (stage, CxxStage):
                utils.cxx.CxxBuilder (stage.target, stage.compiler, stage.ubuntu_version).run ()
            elif isinstance (stage, BootstrapStage):
                utils.bootstrap.VxxBuilder (
                    prev_gyc=stage.prev_gyc,
                    prev_gyllir=stage.prev_gyllir,
                    versions=stage.versions,
                    ubuntu_version=stage.ubuntu_version,
                ).run ()

            if stage.gyllir is not None:
                utils.gyllir.GyllirBuilder (
                    gyc=stage.gyllir.gyc,
                    compile_with=stage.gyllir.compile_with,
                    gyllir_version=stage.gyllir.gyllir_version,
                    ubuntu_version=stage.gyllir.ubuntu_version,
                ).run ()
