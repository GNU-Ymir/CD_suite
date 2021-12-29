export INSTALL_DIR=/home/vagrant

mkdir ${INSTALL_DIR}/gymir/
cd ${INSTALL_DIR}/gymir/
mkdir ${INSTALL_DIR}/gymir/gcc-src

cd ${INSTALL_DIR}/gymir/
git clone --depth=1 git://gcc.gnu.org/git/gcc.git gcc-src
cd ${INSTALL_DIR}/gymir/gcc-src
git fetch --tags --depth=1
git checkout releases/gcc-9.3.0

cd ${INSTALL_DIR}/gymir/gcc-src/gcc/
git clone --depth=1 https://github.com/GNU-Ymir/gymir.git ymir
