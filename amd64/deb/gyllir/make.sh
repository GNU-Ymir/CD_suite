export INSTALL_DIR=/home/vagrant

rm -rf ${INSTALL_DIR}/gyllir/
mkdir ${INSTALL_DIR}/gyllir/
mkdir ${INSTALL_DIR}/gyllir/bin
mkdir ${INSTALL_DIR}/gyllir/install

cd ${INSTALL_DIR}/gyllir
git clone https://github.com/GNU-Ymir/Gyllir.git src

sudo dpkg -i ${INSTALL_DIR}/gymir/gcc-bin/*.deb
sudo dpkg -i ${INSTALL_DIR}/midgard/bin/*.deb

cd ${INSTALL_DIR}/gyllir/src/
mkdir .build
cd .build
cmake ..
make -j4

mkdir -p ${INSTALL_DIR}/gyllir/install/etc/bash_completion.d/
mkdir -p ${INSTALL_DIR}/gyllir/install/usr/bin

cp ${INSTALL_DIR}/gyllir/src/bash/_gyllir ${INSTALL_DIR}/gyllir/install/etc/bash_completion.d/_gyllir
cp ${INSTALL_DIR}/gyllir/src/.build/gyllir ${INSTALL_DIR}/gyllir/install/usr/bin/gyllir
cd ${INSTALL_DIR}/gyllir/bin/
fpm -s dir -t deb -n gyllir -v 0.1.0 -C ${INSTALL_DIR}/gyllir/install \
	-p gyllir_VERSION_ARCH.deb \
	-d "gyc-9" \
        -d "libgmidgard-9" \
	usr/bin/gyllir etc/bash_completion.d/_gyllir

