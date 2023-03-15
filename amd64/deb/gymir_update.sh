GCC_VERSION=$1
GCC_MAJOR_VERSION=$(cut -d '.' -f 1 <<< $GCC_VERSION)
INSTALL_DIR=$2

echo $GCC_VERSION
echo $GCC_MAJOR_VERSION



rm -rf ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-install
mkdir ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-install

cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-src/gcc/ymir/
git pull origin master

cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-build/
rm gcc/ymir/*.o
rm prev-gcc/ymir/*.o
make 
make install DESTDIR=${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-install/

rm -rf ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/
mkdir ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/
cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/

mkdir -p ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb/usr/bin
mkdir -p ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb/usr/lib/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/

cp ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-install/usr/bin/x86_64-linux-gnu-gyc-${GCC_MAJOR_VERSION} ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb/usr/bin
cp ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-install/usr/lib/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/ymir1 ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb/usr/lib/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/ymir1

ln -s x86_64-linux-gnu-gyc-${GCC_MAJOR_VERSION} ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb/usr/bin/gyc-${GCC_MAJOR_VERSION}
ln -s gyc-${GCC_MAJOR_VERSION} ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb/usr/bin/gyc


mkdir ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb/DEBIAN
CONTROL_FILE=${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb/DEBIAN/control

cat >$CONTROL_FILE <<EOF
Package: gyc-${GCC_MAJOR_VERSION}
Version: ${GCC_VERSION}
Architecture: amd64
Maintainer: ecadorel@gmail.com
Description: gnu ymir compiler
Depends: g++-${GCC_MAJOR_VERSION} (>= $GCC_MAJOR_VERSION), gcc-${GCC_MAJOR_VERSION} (>= $GCC_MAJOR_VERSION), libgc-dev, libdwarf-dev
EOF

dpkg-deb --build ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb
mv ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb.deb ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gyc_${GCC_VERSION}_amd64.deb

sudo dpkg -i ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gyc_${GCC_VERSION}_amd64.deb
cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/

rm -rf ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/midgard/
git clone https://github.com/GNU-Ymir/yruntime.git midgard
cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/midgard/
mkdir .build
cd .build

cmake ..
make -j4

make install DESTDIR=${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb
mkdir -p ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb/usr/lib/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir/

cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/midgard/
cp -r core ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb/usr/lib/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir/
cp -r std ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb/usr/lib/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir/
cp -r etc ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb/usr/lib/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir/

dpkg-deb --build ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb
mv ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-deb.deb ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gyc_${GCC_VERSION}_amd64.deb

