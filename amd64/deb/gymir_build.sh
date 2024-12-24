GCC_VERSION=$1
GCC_MAJOR_VERSION=$(cut -d '.' -f 1 <<< $GCC_VERSION)
INSTALL_DIR=$2
YMIR_VERSION=$3

echo $GCC_VERSION
echo $GCC_MAJOR_VERSION

mkdir -p ${INSTALL_DIR}

sudo apt-get -y update
sudo apt-get install -y --no-install-recommends sudo pkg-config git build-essential software-properties-common aspcud unzip curl wget
sudo apt-get install -y --no-install-recommends gcc g++ flex autoconf automake libtool cmake emacs patchelf
sudo apt-get install -y --no-install-recommends gcc-multilib g++-multilib libgc-dev libgmp-dev libbfd-dev zlib1g-dev
sudo apt-get install -y build-essential

mkdir ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/
cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/
mkdir ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-src

cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/
git clone --depth=1 git://gcc.gnu.org/git/gcc.git gcc-src
cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-src
git fetch --tags --depth=1
git switch releases/gcc-${GCC_VERSION} --detach

cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-src/gcc/
git clone --depth=1 https://github.com/GNU-Ymir/gymir.git ymir

cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-src/gcc/ymir
git fetch --all --tags
git checkout ${YMIR_VERSION}
git pull origin ${YMIR_VERSION}

touch ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-src/gcc/ymir/lang.opt.urls

cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-src/

rm -rf ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-build
mkdir ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-build

# ./contrib/download_prerequisites

cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-build/
../gcc-src/configure --enable-languages=c,d,ymir --with-gcc-major-version-only --program-suffix=-${GCC_MAJOR_VERSION} --prefix=/usr --program-prefix=x86_64-linux-gnu- --libexecdir=/usr/libexec --libdir=/usr/lib --with-sysroot=/ --with-arch-directory=amd64 --enable-multiarch --with-arch-32=i686 --with-abi=m64 --with-multilib-list=m32,m64,mx32 --enable-multilib --enable-checking=release --build=x86_64-linux-gnu --host=x86_64-linux-gnu --target=x86_64-linux-gnu --disable-bootstrap

rm -rf ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-install
mkdir ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-install

cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-build/
rm gcc/ymir/*.o
rm prev-gcc/ymir/*.o
make -j12
make install DESTDIR=${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-install/

rm -rf ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/
mkdir ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/
cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/

mkdir -p ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/usr/bin
mkdir -p ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/usr/lib/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/
mkdir -p ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/

cp ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-install/usr/bin/x86_64-linux-gnu-gyc-${GCC_MAJOR_VERSION} ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/usr/bin
cp ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-install/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/ymir1 ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/ymir1

ln -s x86_64-linux-gnu-gyc-${GCC_MAJOR_VERSION} ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/usr/bin/gyc-${GCC_MAJOR_VERSION}
ln -s gyc-${GCC_MAJOR_VERSION} ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/usr/bin/gyc


mkdir ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/DEBIAN
CONTROL_FILE=${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/DEBIAN/control

cat >$CONTROL_FILE <<EOF
Package: gyc-${GCC_MAJOR_VERSION}
Version: ${GCC_VERSION}
Architecture: amd64
Maintainer: ecadorel@gmail.com
Description: gnu ymir compiler
Depends: g++-${GCC_MAJOR_VERSION} (>= $GCC_MAJOR_VERSION), gcc-${GCC_MAJOR_VERSION} (>= $GCC_MAJOR_VERSION), libgc-dev, libdwarf-dev
EOF

dpkg-deb --build ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin
mv ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin.deb ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gyc_${GCC_VERSION}_amd64.deb

sudo dpkg -i ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gyc_${GCC_VERSION}_amd64.deb
cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/

# git clone https://github.com/GNU-Ymir/yruntime.git midgard
cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/midgard/
git fetch --all --tags
git checkout ${YMIR_VERSION}
mkdir .build
cd .build

cmake ..
make -j12

make install DESTDIR=${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin
mkdir -p ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir/

cd ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/midgard/
cp -r core ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir/
cp -r std ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir/
cp -r etc ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir/

dpkg-deb --build ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin
mv ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gcc-bin.deb ${INSTALL_DIR}/gyc-${GCC_VERSION}-build/gyc_${GCC_VERSION}_amd64.deb
