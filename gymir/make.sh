export INSTALL_DIR=/home/vagrant

rm -rf ${INSTALL_DIR}/gymir/gcc-install
mkdir ${INSTALL_DIR}/gymir/gcc-install

cd ${INSTALL_DIR}/gymir/gcc-build/
rm gcc/ymir/*.o
rm prev-gcc/ymir/*.o
make 
make install DESTDIR=${INSTALL_DIR}/gymir/gcc-install/
