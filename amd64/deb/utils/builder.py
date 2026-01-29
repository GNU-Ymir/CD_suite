#!/usr/bin/env python3

import yaml
import utils.cxx
import utils.boot
import utils.gyllir
import requests
import os


urlGyllir = {
    "cxx" : "https://github.com/GNU-Ymir/Gyllir/releases/download/v_cxx/cxx_gyllir_amd64.deb",
    "v0.1" : "https://github.com/GNU-Ymir/Gyllir/releases/download/v0.1_tag/v0.1_gyllir_amd64.deb",
    "v1.0" : "https://github.com/GNU-Ymir/Gyllir/releases/download/v1.0_tag/v1.0_gyllir_amd64.deb",
    "v1.1" : "https://github.com/GNU-Ymir/Gyllir/releases/download/v1.1.0/v1.1_gyllir_amd64.deb"
}

urlGyc = {
    "v1.1" : {
        "13.2.0" : "https://github.com/GNU-Ymir/gymir/releases/download/v1.1.0/v1.1_gyc_13.2.0_amd64.deb" 
    },
    "v0.1" : {
        "13.2.0" : "https://github.com/GNU-Ymir/gymir/releases/download/v0.1_tag/v0.1_gyc_13.2.0_amd64.deb" 
    },
    "v1.0" : {
        "13.2.0" : "https://github.com/GNU-Ymir/gymir/releases/download/v1.0_tag/v1.0_gyc_13.2.0_amd64.deb" 
    },    
    "cxx" : {
        "13.2.0" : "https://github.com/GNU-Ymir/gymir/releases/download/cxx_version_13.2.0/cxx_gyc_13.2.0_amd64.deb" 
    }
}

class Builder :

    def __init__ (self, config):
        with open(config, 'r') as file :
            self._cfg = yaml.safe_load (file)
            self._gcc_version = self._cfg ["gcc_version"]
            self._versions = self._cfg ["ymir_versions"]

    def wget (self, url, where) :
        print (f"Downloading : {where} from {url}")
        r = requests.get(url)
        open(where , 'wb').write(r.content)
        print (f"Downloading : {where} from {url}. Done.")
            
    def ensureVersionPresent (self, version, gcc_version):
        gycDeb = f"results/{version}_gyc_{gcc_version}_amd64.deb"
        gyllirDeb = f"results/{version}_gyllir_amd64.deb"
                
        if not os.path.isfile(gyllirDeb):
            if version not in urlGyllir :
                print (f"Failed to download gyllir deb")
                raise Exception ("Failed");
                
            self.wget (urlGyllir [version], gyllirDeb)            

        if not os.path.isfile(gycDeb):
            if version not in urlGyc or gcc_version not in urlGyc [version] :
                print (f"Failed to download gyc deb")
                raise Exception ("Failed");

            self.wget (urlGyc [version][gcc_version], gycDeb)                        
            
    def run (self):
        try:
            os.mkdir(f"results")
            print(f"Directory '{directory_name}' created successfully.")
        except Exception:
            pass
        
        for v in self._versions:
            if v == "cxx_version":
                utils.cxx.CxxBuilder (self._gcc_version).run ()
                utils.gyllir.GyllirBuilder (self._gcc_version, "cxx").run ()
            elif v == "bootstrap_v0.1" :
                self.ensureVersionPresent ("cxx", self._gcc_version)
                utils.boot.BootstrapBuilder (self._gcc_version, "cxx", "v0.1").run ()
                utils.gyllir.GyllirBuilder (self._gcc_version, "v0.1").run ()
            elif v == "bootstrap_v1.0":
                self.ensureVersionPresent ("v0.1", self._gcc_version)
                utils.boot.BootstrapBuilder (self._gcc_version, "v0.1", "v1.0").run ()
                utils.gyllir.GyllirBuilder (self._gcc_version, "v1.0").run ()
            elif v == "bootstrap_v1.1":
                self.ensureVersionPresent ("v1.0", self._gcc_version)
                utils.boot.BootstrapBuilder (self._gcc_version, "v1.0", "v1.1").run ()
                utils.gyllir.GyllirBuilder (self._gcc_version, "v1.1").run ()
            elif v == "bootstrap_v1.1_alone":
                self.ensureVersionPresent ("v1.1", self._gcc_version)
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
