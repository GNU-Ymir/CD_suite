export INSTALL_DIR=/home/vagrant

rm -rf ${INSTALL_DIR}/midgard/
mkdir ${INSTALL_DIR}/midgard/
mkdir ${INSTALL_DIR}/midgard/install
mkdir ${INSTALL_DIR}/midgard/bin

cd ${INSTALL_DIR}/midgard/
git clone https://github.com/GNU-Ymir/yruntime.git runtime

sudo dpkg -i ${INSTALL_DIR}/gymir/gcc-bin/gyc-*.deb

cd ${INSTALL_DIR}/midgard/runtime/runtime/
mkdir .build
cd .build

cmake ..
make -j4
make install DESTDIR=${INSTALL_DIR}/midgard/install

cd ${INSTALL_DIR}/midgard/runtime/midgard
mkdir .build
cd .build
cmake ..
make -j4
make install DESTDIR=${INSTALL_DIR}/midgard/install

cd ..
mkdir -p ${INSTALL_DIR}/midgard/install/usr/lib/gcc/x86_64-linux-gnu/9/include/ymir/
cp -r core ${INSTALL_DIR}/midgard/install/usr/lib/gcc/x86_64-linux-gnu/9/include/ymir/
cp -r std ${INSTALL_DIR}/midgard/install/usr/lib/gcc/x86_64-linux-gnu/9/include/ymir/
cp -r etc ${INSTALL_DIR}/midgard/install/usr/lib/gcc/x86_64-linux-gnu/9/include/ymir/

cd ${INSTALL_DIR}/midgard/bin
fpm -s dir -t deb -n libgmidgard-9 -v 9.3.0 -C ${INSTALL_DIR}/midgard/install \
	-p libgmidgard_VERSION_ARCH.deb \
	-d "libgc-dev >= 1.3.2" \
        -d "libbfd-dev" \
	-d "libc6 >= 2.31" \
	-d "gcc-9-base >= 9" \
	-d "libgcc1" \
	-d "zlib1g >= 1:1.2.0" \
	usr/lib

