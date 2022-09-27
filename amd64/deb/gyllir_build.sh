INSTALL_DIR=$1

rm -rf ${INSTALL_DIR}/gyllir/
mkdir ${INSTALL_DIR}/gyllir/
mkdir ${INSTALL_DIR}/gyllir/bin
mkdir ${INSTALL_DIR}/gyllir/install

cd ${INSTALL_DIR}/gyllir
git clone https://github.com/GNU-Ymir/Gyllir.git src

cd ${INSTALL_DIR}/gyllir/src/
mkdir .build
cd .build
cmake ..
make -j4

mkdir -p ${INSTALL_DIR}/gyllir/install/etc/bash_completion.d/
mkdir -p ${INSTALL_DIR}/gyllir/install/usr/bin

cp ${INSTALL_DIR}/gyllir/src/bash/_gyllir ${INSTALL_DIR}/gyllir/install/etc/bash_completion.d/_gyllir
cp ${INSTALL_DIR}/gyllir/src/.build/gyllir ${INSTALL_DIR}/gyllir/install/usr/bin/gyllir

mkdir ${INSTALL_DIR}/gyllir/install/DEBIAN
CONTROL_FILE=${INSTALL_DIR}/gyllir/install/DEBIAN/control

cat >$CONTROL_FILE <<EOF
Package: gyllir
Version: 0.1.0
Architecture: amd64
Maintainer: ecadorel@gmail.com
Description: gnu ymir project manager
EOF

dpkg-deb --build ${INSTALL_DIR}/gyllir/install
mv ${INSTALL_DIR}/gyllir/install.deb ${INSTALL_DIR}/gyllir/gyllir_0.1.0.deb
