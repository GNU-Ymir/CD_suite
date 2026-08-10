ARG GCC_VERSION="15"
ARG GCC_MAJOR_VERSION="15"
ARG COMPILER_MAJOR_VERSION="15"
ARG YMIR_VERSION="0.1.0"
ARG GYC_VERSION="0.1.0"
ARG MIDGARD_VERSION="0.1.0"
ARG ARCH="amd64"
ARG CLONE_IMAGE="gyc:gcc_clone_26.04"
ARG UBUNTU_VERSION="26.04"

FROM ${CLONE_IMAGE} AS fetch_gcc_version

ARG GCC_VERSION
ARG YMIR_VERSION
ARG GYC_VERSION
ARG GCC_MAJOR_VERSION
ARG COMPILER_MAJOR_VERSION
ARG MIDGARD_VERSION

COPY gyc.deb .
COPY gyllir.deb .
RUN dpkg -i gyc.deb
RUN dpkg -i gyllir.deb

RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc-${COMPILER_MAJOR_VERSION} g++-${COMPILER_MAJOR_VERSION}

RUN gyc --version
RUN gyllir -h || true

WORKDIR /gcc/gcc-src

RUN git fetch origin releases/gcc-${GCC_VERSION}:refs/releases/gcc-${GCC_VERSION} --depth=1
RUN git switch refs/releases/gcc-${GCC_VERSION} --detach

WORKDIR /gcc/gcc-src/gcc
RUN git clone https://github.com/GNU-Ymir/gymir.git ymir

WORKDIR /gcc/gcc-src/gcc/ymir
RUN git fetch --all

RUN git checkout "${GYC_VERSION}";
RUN grep -qF 'ymir/gycspec.o: $(CORETYPES_H) $(PLUGIN_HEADERS) $(INSN_ATTR_H)' Make-lang.in || sed -i '/^CFLAGS-ymir/a ymir/gycspec.o: $(CORETYPES_H) $(PLUGIN_HEADERS) $(INSN_ATTR_H)' Make-lang.in

RUN touch lang.opt.urls
RUN git clone https://github.com/GNU-Ymir/bootstrap.git

WORKDIR /gcc/gcc-src/gcc/ymir/bootstrap
RUN git switch ${YMIR_VERSION} --detach

# Keep the compiled ymirc's baked-in include-path constant (MIDGARD_VERSION in
# src/ymirc/global/common.yr, set from this file by tools/set-version.sh, wired as a
# gyllir pre-build command) in sync with the midgard release this pipeline actually pairs
# with this gyc release (the MIDGARD_VERSION arg, checked out below in build_midgard) -
# the tag's own committed YMIR_VERSION would otherwise be free to drift from what the
# CD_suite version matrix (versions.py) intends for this stage. Older tags may not have a
# YMIR_VERSION file (pre-dates tools/set-version.sh) - leave those untouched.
RUN if [ -f YMIR_VERSION ]; then \
		grep -q '^MIDGARD_VERSION=' YMIR_VERSION \
			&& sed -i "s/^MIDGARD_VERSION=.*/MIDGARD_VERSION=${MIDGARD_VERSION}/" YMIR_VERSION \
			|| echo "MIDGARD_VERSION=${MIDGARD_VERSION}" >> YMIR_VERSION; \
	fi

WORKDIR /gcc/gcc-src/
RUN ./contrib/download_prerequisites

FROM fetch_gcc_version AS configure

ARG GCC_VERSION
ARG YMIR_VERSION
ARG GCC_MAJOR_VERSION
ARG COMPILER_MAJOR_VERSION

ARG BREAK=0
WORKDIR /gcc/gcc-build
RUN CC=gcc-${COMPILER_MAJOR_VERSION} CXX=g++-${COMPILER_MAJOR_VERSION} ../gcc-src/configure --enable-languages=c,d,ymir --with-gcc-major-version-only --program-suffix=-${GCC_MAJOR_VERSION} --prefix=/usr --program-prefix=x86_64-linux-gnu- --libexecdir=/usr/libexec --libdir=/usr/lib --with-sysroot=/ --with-arch-directory=amd64 --enable-multiarch --with-arch-32=i686 --with-abi=m64 --with-multilib-list=m32,m64,mx32 --enable-multilib --enable-checking=release --build=x86_64-linux-gnu --host=x86_64-linux-gnu --target=x86_64-linux-gnu --disable-bootstrap

FROM configure AS make
WORKDIR /gcc/gcc-build

RUN make -j$(( $(nproc) - 1 ))
RUN make install DESTDIR=/gcc/gcc-install

FROM make AS build_first_deb

ARG GCC_VERSION
ARG GCC_MAJOR_VERSION
ARG YMIR_VERSION

WORKDIR /gcc
RUN mkdir -p gcc-bin/DEBIAN
RUN mkdir -p gcc-bin/usr/bin
RUN mkdir -p gcc-bin/usr/lib/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}
RUN mkdir -p gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}

RUN ls /gcc/gcc-install/usr/bin/
RUN cp /gcc/gcc-install/usr/bin/x86_64-linux-gnu-gyc-${GCC_MAJOR_VERSION} /gcc/gcc-bin/usr/bin/
RUN cp /gcc/gcc-install/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/ymir1 /gcc/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/ymir1

WORKDIR /gcc/gcc-bin/usr/bin
RUN ln -s x86_64-linux-gnu-gyc-${GCC_MAJOR_VERSION} gyc-${GCC_MAJOR_VERSION}
RUN ln -s gyc-${GCC_MAJOR_VERSION} gyc

WORKDIR /gcc/gcc-bin/DEBIAN
COPY control.in /gcc/gcc-bin/DEBIAN/control
RUN sed -i "s/@GCC_MAJOR_VERSION@/${GCC_MAJOR_VERSION}/g" /gcc/gcc-bin/DEBIAN/control 
RUN sed -i "s/@GCC_VERSION@/${GCC_VERSION}/g" /gcc/gcc-bin/DEBIAN/control

WORKDIR /gcc
RUN find gcc-bin
RUN cat gcc-bin/DEBIAN/control
RUN dpkg --build gcc-bin

FROM ubuntu:${UBUNTU_VERSION} AS build_midgard

ARG GCC_VERSION
ARG GCC_MAJOR_VERSION
ARG YMIR_VERSION
ARG MIDGARD_VERSION

WORKDIR /gcc

RUN apt-get update
RUN apt-get install -y gcc-${GCC_MAJOR_VERSION} g++-${GCC_MAJOR_VERSION} flex autoconf automake libtool cmake patchelf libdwarf-dev git libgc-dev

RUN mkdir gcc-bin
RUN mkdir -p gcc-bin/DEBIAN
RUN mkdir -p gcc-bin/usr/bin
RUN mkdir -p gcc-bin/usr/lib/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}
RUN mkdir -p gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}
COPY --from=build_first_deb gcc/gcc-install/usr/bin/x86_64-linux-gnu-gyc-${GCC_MAJOR_VERSION} gcc-bin/usr/bin/
COPY --from=build_first_deb gcc/gcc-install/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/ymir1 gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/ymir1

COPY --from=build_first_deb /gcc/gcc-bin.deb .
RUN dpkg -i gcc-bin.deb

ARG CACHE_BREAK=3
RUN git clone https://github.com/GNU-Ymir/yruntime.git 

WORKDIR /gcc/yruntime
RUN git fetch --all --tags
RUN git checkout "${MIDGARD_VERSION}";

# midgard's own CMakeLists.txt names the built libs/install dir after the major.minor of
# YMIR_BOOTSTRAP_VERSION in this checkout's YMIR_VERSION file - not after the MIDGARD_VERSION
# release tag itself, and the two can drift (e.g. this stage's bootstrap=1.2.0 vs
# midgard=1.2.1). Read the same file CMake reads instead of re-deriving it from the tag.
RUN sed -nE 's/^YMIR_BOOTSTRAP_VERSION=([0-9]+\.[0-9]+).*/\1/p' YMIR_VERSION > /tmp/midgard_short_version
RUN test -s /tmp/midgard_short_version || (echo "could not derive MIDGARD_SHORT_VERSION from $(pwd)/YMIR_VERSION" >&2 && exit 1)

RUN mkdir .build

WORKDIR /gcc/yruntime/.build
RUN touch __lib_test_.o
RUN touch __lib_debug_.o
RUN touch __lib_release_.o

RUN cmake ..
RUN make 
RUN make install DESTDIR=/gcc/gcc-bin

WORKDIR /gcc/yruntime/midgard

RUN MIDGARD_SHORT_VERSION="$(cat /tmp/midgard_short_version)" && echo "$MIDGARD_SHORT_VERSION" \
	&& mkdir -p /gcc/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir/$MIDGARD_SHORT_VERSION \
	&& cp -r * /gcc/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir/$MIDGARD_SHORT_VERSION

WORKDIR /gcc/gcc-bin/usr/lib
RUN MIDGARD_SHORT_VERSION="$(cat /tmp/midgard_short_version)" \
	&& ln -s libgymidgard-debug_$MIDGARD_SHORT_VERSION.a libgymidgard-debug.a \
	&& ln -s libgymidgard-tests_$MIDGARD_SHORT_VERSION.a libgymidgard-tests.a \
	&& ln -s libgymidgard-release_$MIDGARD_SHORT_VERSION.a libgymidgard-release.a

WORKDIR /gcc/gcc-bin/DEBIAN

COPY control.in /gcc/gcc-bin/DEBIAN/control
RUN sed -i "s/@GCC_MAJOR_VERSION@/${GCC_MAJOR_VERSION}/g" /gcc/gcc-bin/DEBIAN/control 
RUN sed -i "s/@GCC_VERSION@/${GCC_VERSION}/g" /gcc/gcc-bin/DEBIAN/control
 
WORKDIR /gcc/gcc-bin/usr/bin
RUN ln -s x86_64-linux-gnu-gyc-${GCC_MAJOR_VERSION} gyc-${GCC_MAJOR_VERSION}
RUN ln -s gyc-${GCC_MAJOR_VERSION} gyc

WORKDIR /gcc
RUN dpkg --build gcc-bin

ARG ARCH 
RUN mv gcc-bin.deb /gyc-${GCC_MAJOR_VERSION}_${YMIR_VERSION}_${ARCH}.deb

FROM scratch AS export

ARG GCC_VERSION
ARG GCC_MAJOR_VERSION
ARG YMIR_VERSION
ARG ARCH

COPY --from=build_midgard /gyc-${GCC_MAJOR_VERSION}_${YMIR_VERSION}_${ARCH}.deb /
CMD ["true"]
