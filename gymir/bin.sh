export INSTALL_DIR=/home/vagrant

rm -rf ${INSTALL_DIR}/gymir/gcc-bin/
mkdir ${INSTALL_DIR}/gymir/gcc-bin/
cd ${INSTALL_DIR}/gymir/gcc-bin/

ln -s x86_64-linux-gnu-gyc-9 ${INSTALL_DIR}/gymir/gcc-install/usr/bin/gyc-9
ln -s gyc-9 ${INSTALL_DIR}/gymir/gcc-install/usr/bin/gyc

fpm -s dir -t deb -n gyc-9 -v 9.3.0 -C ${INSTALL_DIR}/gymir/gcc-install \
	-p gyc-9_VERSION_ARCH.deb \
	-d "g++-9 >= 9" \
	-d "gcc-9-base >= 9" \
	-d "libc6 >= 2.31" \
	-d "libgmp10 >= 2:6.2.0~" \
	-d "libmpc3" \
	-d "libmpfr6 >= 4.0.2" \
	-d "zlib1g >= 1:1.2.0" \
	usr/bin/gyc-9 usr/bin/gyc usr/bin/x86_64-linux-gnu-gyc-9 usr/lib/gcc/x86_64-linux-gnu/9/ymir1 

