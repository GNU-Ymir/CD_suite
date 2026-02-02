#!/usr/bin/env python3

import utils.vm

CONTROL = """
Package: gyllir
Version: 0.1.0
Architecture: amd64
Maintainer: ecadorel
Description: gnu ymir project manager
"""


class GyllirBuilder:
    def __init__ (self, gcc_version, gyc_version, tag):
        self._gcc_version = gcc_version
        self._gcc_major_version = gcc_version.split (".")[0]
        self._version = gyc_version
        self._tag = tag
        self._vm = utils.vm.VMLauncher (self._version)

    # Run the builder and generate the
    def run (self) :
        print (f"Building Gyllir version {self._version}")
        self._vm.destroy ()
        self._vm.boot ()
        self._installDependencies ()
        self._cloneRepo ()
        self._make ()
        self._createDebFile ()
        self._vm.halt ()
        self._vm.destroy ()

    # Install the dependencies required by the cxx builder
    def _installDependencies (self):
        self._vm.runCmd ("sudo apt-get install -y --no-install-recommends sudo pkg-config git build-essential software-properties-common aspcud unzip curl wget")
        self._vm.runCmd ("sudo apt-get install -y --no-install-recommends gcc g++ flex autoconf automake libtool cmake patchelf libdwarf-dev")
        self._vm.runCmd ("sudo apt-get install -y --no-install-recommends gcc-multilib g++-multilib libgc-dev libgmp-dev libbfd-dev zlib1g-dev gdc")
        self._vm.runCmd ("sudo apt-get install -y build-essential")
        self._vm.uploadFile (f"../results/{self._version}_gyc_{self._gcc_version}_amd64.deb", "gyc.deb")
        self._vm.runCmd ("sudo dpkg -i ./gyc.deb")

    # Clone the gyllir repo
    def _cloneRepo (self):
        self._vm.runCmd ("git clone https://github.com/GNU-Ymir/Gyllir.git gyllir")
        self._vm.runCmd ("cd gyllir && git fetch --all --tags")
        self._vm.runCmd (f"cd gyllir && git checkout {self._tag}")
        self._vm.runCmd (f"cd gyllir && git pull origin {self._tag}")

        self._vm.runCmd ("cd gyllir && mkdir .build")
        self._vm.runCmd ("cd gyllir/.build && cmake ..")

    # Make the compiler
    def _make (self) :
        self._vm.runCmd ("mkdir install")
        self._vm.runCmd ("cd gyllir/.build && make -j4")
        self._vm.runCmd ("cd gyllir/.build && make install DESTDIR=/home/vagrant/install")

    # Create the deb file
    def _createDebFile (self):
        self._vm.runCmd ("mkdir -p install/etc/bash_completion.d")
        self._vm.runCmd ("mkdir -p install/usr/bin")
        self._vm.runCmd ("mkdir -p install/DEBIAN")
        self._vm.runCmd ("cp gyllir/bash/_gyllir /home/vagrant/install/etc/bash_completion.d")
        self._vm.runCmd ("cp gyllir/.build/gyllir /home/vagrant/install/usr/bin/")
        self._vm.runCmd ("chmod +x /home/vagrant/install/usr/bin/gyllir")
        with open (f".{self._version}/control", "w") as f:
            f.write (CONTROL)

        self._vm.uploadFile ("control", "install/DEBIAN/control")
        self._vm.runCmd ("dpkg --build install")

        self._vm.downloadFile ("install.deb", f"../results/{self._version}_gyllir_amd64.deb")
