#!/usr/bin/env python3

import utils.vm

CONTROL = """
Package: gyc-{GCC_MAJOR_VERSION}
Version: {GCC_VERSION}
Maintainer: ecadorel
Architecture: amd64
Description: gnu ymir compiler
Depends: g++-{GCC_MAJOR_VERSION} (>= {GCC_MAJOR_VERSION}), gcc-{GCC_MAJOR_VERSION} (>= {GCC_MAJOR_VERSION}), libgc-dev, libdwarf-dev
"""


class CxxBuilder:
    def __init__ (self, gcc_version):
        self._gcc_version = gcc_version
        self._gcc_major_version = gcc_version.split (".")[0]
        self._vm = utils.vm.VMLauncher ()
        pass

    # Run the builder and generate the
    def run (self) :
        print ("Building CXX version")
        self._vm.boot ()
        self._installDependencies ()
        self._cloneRepo ()
        self._configureBuild ()
        self._make ()
        self._createFirstDebFile ()
        self._cloneMidgard ()
        self._buildMidgard ()
        self._createFinalDebFile ()

    # Install the dependencies required by the cxx builder
    def _installDependencies (self):
        self._vm.runCmd ("sudo apt-get install -y --no-install-recommends sudo pkg-config git build-essential software-properties-common aspcud unzip curl wget")
        self._vm.runCmd ("sudo apt-get install -y --no-install-recommends gcc g++ flex autoconf automake libtool cmake emacs patchelf libdwarf-dev")
        self._vm.runCmd ("sudo apt-get install -y --no-install-recommends gcc-multilib g++-multilib libgc-dev libgmp-dev libbfd-dev zlib1g-dev gdc")
        self._vm.runCmd ("sudo apt-get install -y build-essential")

    # Clone the GCC repository
    def _cloneRepo (self):
        self._vm.runCmd ("mkdir -p gcc")
        self._vm.runCmd ("mkdir -p gcc/gcc-src")
        self._vm.runCmd ("mkdir -p gcc/gcc-build")
        self._vm.runCmd ("mkdir -p gcc/gcc-bin")
        self._vm.runCmd ("cd gcc/ && git clone --depth=1 git://gcc.gnu.org/git/gcc.git gcc-src")
        self._vm.runCmd ("cd gcc/gcc-src && git fetch --tags --depth=1")
        self._vm.runCmd (f"cd gcc/gcc-src && git switch releases/gcc-{self._gcc_version} --detach")

        self._vm.runCmd ("cd gcc/gcc-src/gcc && git clone https://github.com/GNU-Ymir/gymir.git ymir")
        self._vm.runCmd ("cd gcc/gcc-src/gcc/ymir && git fetch --all")
        self._vm.runCmd ("cd gcc/gcc-src/gcc/ymir && git checkout cxx_version")
        self._vm.runCmd ("cd gcc/gcc-src/gcc/ymir && git pull origin cxx_version")
        self._vm.runCmd ("cd gcc/gcc-src/gcc/ymir && touch lang.opt.urls")

        self._vm.runCmd ("cd gcc/gcc-src/ && ./contrib/download_prerequisites")

    # Configure the build
    def _configureBuild (self) :
        self._vm.runCmd (f"cd gcc/gcc-build && ../gcc-src/configure --enable-languages=c,d,ymir --with-gcc-major-version-only --program-suffix=-{self._gcc_major_version} --prefix=/usr --program-prefix=x86_64-linux-gnu- --libexecdir=/usr/libexec --libdir=/usr/lib --with-sysroot=/ --with-arch-directory=amd64 --enable-multiarch --with-arch-32=i686 --with-abi=m64 --with-multilib-list=m32,m64,mx32 --enable-multilib --enable-checking=release --build=x86_64-linux-gnu --host=x86_64-linux-gnu --target=x86_64-linux-gnu --disable-bootstrap")
        self._vm.runCmd ("cd gcc/gcc-build && rm gcc/ymir/*.o")
        self._vm.runCmd ("cd gcc/gcc-build && rm prev-gcc/ymir/*.o")

    # Make the
    def _make (self):
        self._vm.runCmd ("cd gcc/gcc-build && make")
        self._vm.runCmd ("cd gcc/gcc-build && make install DESTDIR=/home/vagrant/gcc/gcc-install")

    # Create the first deb file before midgard build
    def _createFirstDebFile (self):
        self._vm.runCmd ("mkdir -p gcc/gcc-bin/usr/bin")
        self._vm.runCmd (f"mkdir -p gcc/gcc-bin/usr/lib/gcc/x86_64-linux-gnu/{self._gcc_major_version}")
        self._vm.runCmd (f"mkdir -p gcc/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/{self._gcc_major_version}")
        self._vm.runCmd (f"cp gcc/gcc-install/usr/bin/x86_64-linux-gnu-gyc-{self._gcc_major_version} gcc/gcc-bin/usr/bin/")
        self._vm.runCmd (f"cp gcc/gcc-install/usr/libexec/gcc/x86_64-linux-gnu/{self._gcc_major_version}/ymir1 gcc/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/{self._gcc_major_version}/ymir1")
        self._vm.runCmd (f"cd gcc/gcc-bin/usr/bin && ln -s x86_64-linux-gnu-gyc-{self._gcc_major_version} gyc-{self._gcc_major_version}")
        self._vm.runCmd (f"cd gcc/gcc-bin/usr/bin && ln -s gyc-{self._gcc_major_version} gyc")
        self._vm.runCmd (f"mkdir -p gcc/gcc-bin/DEBIAN")

        with open (".vagrant/control", "w") as f:
            c = CONTROL.replace ("{GCC_MAJOR_VERSION}", self._gcc_major_version)
            c = c.replace ("{GCC_VERSION}", self._gcc_version)
            f.write (c)

        self._vm.uploadFile ("control", "gcc/gcc-bin/DEBIAN/control")
        self._vm.runCmd ("dpkg --build gcc/gcc-bin")
        self._vm.runCmd (f"sudo dpkg -i gcc/gcc-bin.deb")

    # Clone the midgard library
    def _cloneMidgard (self):
        self._vm.runCmd (f"cd gcc/ && git clone https://github.com/GNU-Ymir/yruntime.git midgard")
        self._vm.runCmd (f"cd gcc/midgard && git fetch --all --tags")
        self._vm.runCmd (f"cd gcc/midgard && git checkout cxx_version")


    # Build the midgard library
    def _buildMidgard (self):
        self._vm.runCmd (f"cd gcc/midgard && mkdir .build")
        self._vm.runCmd (f"cd gcc/midgard/.build && cmake ..")
        self._vm.runCmd (f"cd gcc/midgard/.build && make -j4")
        self._vm.runCmd (f"cd gcc/midgard/.build && make install DESTDIR=/home/vagrant/gcc/gcc-bin")

    # Create the final deb file and download it
    def _createFinalDebFile (self):
        self._vm.runCmd (f"mkdir -p /home/vagrant/gcc/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/{self._gcc_major_version}/include/ymir/")
        self._vm.runCmd (f"cd gcc/midgard && cp -r core /home/vagrant/gcc/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/{self._gcc_major_version}/include/ymir/")
        self._vm.runCmd (f"cd gcc/midgard && cp -r std /home/vagrant/gcc/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/{self._gcc_major_version}/include/ymir/")
        self._vm.runCmd (f"cd gcc/midgard && cp -r etc /home/vagrant/gcc/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/{self._gcc_major_version}/include/ymir/")
        self._vm.runCmd ("dpkg --build gcc/gcc-bin")
        self._vm.downloadFile ("gcc/gcc-bin.deb", f"../gyc_{self._gcc_version}_amd64.deb")
