export INSTALL_DIR=/home/vagrant

cd ${INSTALL_DIR}/gymir/gcc-src/

rm -rf ${INSTALL_DIR}/gymir/gcc-build
mkdir ${INSTALL_DIR}/gymir/gcc-build

./contrib/download_prerequisites

cd ${INSTALL_DIR}/gymir/gcc-build/
../gcc-src/configure --enable-languages=c,ymir --with-gcc-major-version-only --program-suffix=-9 --prefix=/usr --program-prefix=x86_64-linux-gnu- --libexecdir=/usr/lib --libdir=/usr/lib --with-sysroot=/ --with-arch-directory=amd64 --enable-multiarch --with-arch-32=i686 --with-abi=m64 --with-multilib-list=m32,m64,mx32 --enable-multilib --enable-checking=release --build=x86_64-linux-gnu --host=x86_64-linux-gnu --target=x86_64-linux-gnu
