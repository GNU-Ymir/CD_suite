ARG UBUNTU_VERSION="26.04"
FROM ubuntu:${UBUNTU_VERSION} AS clone_gcc

# apt-get update has to stay in the same RUN as every install it feeds: on its own it becomes a
# cached layer holding an index that keeps naming exact .deb versions long after Ubuntu has dropped
# them from the pool, and the installs then fail with 404s on files that no longer exist.
RUN apt-get update \
	&& apt-get install -y --no-install-recommends sudo pkg-config git build-essential software-properties-common aspcud unzip curl wget \
	&& apt-get install -y --no-install-recommends gcc g++ flex autoconf automake libtool cmake patchelf libdwarf-dev \
	&& apt-get install -y --no-install-recommends gcc-multilib g++-multilib libgc-dev libgmp-dev libbfd-dev zlib1g-dev gdc \
	&& apt-get install -y build-essential

WORKDIR /gcc
RUN mkdir -p gcc-src
RUN mkdir -p gcc-build
RUN mkdir -p gcc-bin

RUN git clone --depth=1 git://gcc.gnu.org/git/gcc.git gcc-src


