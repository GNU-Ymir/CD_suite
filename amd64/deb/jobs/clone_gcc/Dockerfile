ARG UBUNTU_VERSION="26.04"
FROM ubuntu:${UBUNTU_VERSION} AS clone_gcc

RUN apt-get update
RUN apt-get install -y --no-install-recommends sudo pkg-config git build-essential software-properties-common aspcud unzip curl wget
RUN apt-get install -y --no-install-recommends gcc g++ flex autoconf automake libtool cmake patchelf libdwarf-dev
RUN apt-get install -y --no-install-recommends gcc-multilib g++-multilib libgc-dev libgmp-dev libbfd-dev zlib1g-dev gdc
RUN apt-get install -y build-essential

WORKDIR /gcc
RUN mkdir -p gcc-src
RUN mkdir -p gcc-build
RUN mkdir -p gcc-bin

RUN git clone --depth=1 git://gcc.gnu.org/git/gcc.git gcc-src


