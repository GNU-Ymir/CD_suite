GCC_VERSION=$1
GCC_MAJOR_VERSION=$(cut -d '.' -f 1 <<< $GCC_VERSION)
INSTALL_DIR=$2


rm -rf ${INSTALL_DIR}/midgard/
mkdir ${INSTALL_DIR}/midgard/
mkdir ${INSTALL_DIR}/midgard/install
mkdir ${INSTALL_DIR}/midgard/bin

cd ${INSTALL_DIR}/midgard/
git clone https://github.com/GNU-Ymir/yruntime.git runtime

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
mkdir -p ${INSTALL_DIR}/midgard/install/usr/lib/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir/
cp -r core ${INSTALL_DIR}/midgard/install/usr/lib/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir/
cp -r std ${INSTALL_DIR}/midgard/install/usr/lib/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir/
cp -r etc ${INSTALL_DIR}/midgard/install/usr/lib/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir/

mkdir ${INSTALL_DIR}/midgard/install/DEBIAN
CONTROL_FILE=${INSTALL_DIR}/midgard/install/DEBIAN/control

cat >$CONTROL_FILE <<EOF
Package: libmidgard-${GCC_MAJOR_VERSION}-dev
Version: ${GCC_VERSION}
Architecture: amd64
Maintainer: ecadorel@gmail.com
Description: gnu ymir standard library and runtime
Depends: gyc-${GCC_MAJOR_VERSION} (>= $GCC_MAJOR_VERSION)
EOF

dpkg-deb --build ${INSTALL_DIR}/midgard/install/
mv ${INSTALL_DIR}/midgard/install.deb ${INSTALL_DIR}/midgard/libgmidgard_${GCC_VERSION}_amd64.deb
