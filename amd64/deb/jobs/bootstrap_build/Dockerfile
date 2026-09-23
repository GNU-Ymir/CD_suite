ARG GCC_VERSION="15"
ARG GCC_MAJOR_VERSION="15"
ARG COMPILER_MAJOR_VERSION="15"
ARG YMIR_VERSION="0.1.0"
ARG GYC_VERSION="0.1.0"
ARG MIDGARD_VERSION="0.1.0"
ARG YMIR_BOOTSTRAP_MIDGARD_VERSION=""
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
ARG YMIR_BOOTSTRAP_MIDGARD_VERSION

COPY gyc.deb .
COPY gyllir.deb .
RUN dpkg -i gyc.deb
RUN dpkg -i gyllir.deb

# Kept in one RUN with the install - see the note in jobs/clone_gcc/Dockerfile.
RUN apt-get update \
	&& apt-get install -y --no-install-recommends gcc-${COMPILER_MAJOR_VERSION} g++-${COMPILER_MAJOR_VERSION}

RUN gyc --version
RUN gyllir -h || true

# From gymir 1.7.0 on, ymir1 links -lgymidgard-debug_<major.minor> of the midgard the bootstrap
# source is compiled against (YMIR_BOOTSTRAP_MIDGARD_VERSION, the std bootstrap's gyllir.toml pins -
# see gymir's Make-lang.in YMIR_RUNTIME_LIBS), which is not always the one the previous gyc.deb
# bundles (gyc 1.6.0 ships midgard 1.8, bootstrap 1.7.0 pins 1.9). Upstream downloads that
# runtime from its yruntime release; here it is built from its tag with the previous gyc/gyllir
# installed above - the compiler that yruntime release was built with - since the chain only
# trusts what it has built. Only the debug archive is built: it is all ymir1 links, and like in
# build_midgard below, a library target needs no installed midgard. Empty for tags whose
# runtime the previous gyc.deb already carries.
RUN if [ -n "${YMIR_BOOTSTRAP_MIDGARD_VERSION}" ]; then \
		SHORT="$(echo "${YMIR_BOOTSTRAP_MIDGARD_VERSION}" | sed -nE 's/^([0-9]+\.[0-9]+).*/\1/p')" \
		&& test -n "$SHORT" \
		&& git clone https://github.com/GNU-Ymir/yruntime.git /tmp/bootstrap-midgard \
		&& cd /tmp/bootstrap-midgard \
		&& git checkout "${YMIR_BOOTSTRAP_MIDGARD_VERSION}" \
		&& gyllir build gymidgard_debug \
		&& install -m 644 libgymidgard_debug.a "/usr/lib/libgymidgard-debug_${SHORT}.a" \
		&& cd / && rm -rf /tmp/bootstrap-midgard; \
	fi

WORKDIR /gcc/gcc-src

RUN git fetch origin releases/gcc-${GCC_VERSION}:refs/releases/gcc-${GCC_VERSION} --depth=1
RUN git switch refs/releases/gcc-${GCC_VERSION} --detach

WORKDIR /gcc/gcc-src/gcc
RUN git clone https://github.com/GNU-Ymir/gymir.git ymir

WORKDIR /gcc/gcc-src/gcc/ymir
RUN git fetch --all

RUN git checkout "${GYC_VERSION}";

# A tag that names YMIR_BOOTSTRAP_MIDGARD_VERSION links that midgard's runtime, and would only fail
# at ymir1's final link (a missing -lgymidgard-debug_<version>) if the stage forgot to build it.
RUN if [ -f YMIR_VERSION ] && grep -q '^YMIR_BOOTSTRAP_MIDGARD_VERSION=' YMIR_VERSION && [ -z "${YMIR_BOOTSTRAP_MIDGARD_VERSION}" ]; then \
		echo "gymir ${GYC_VERSION} links the midgard named by YMIR_BOOTSTRAP_MIDGARD_VERSION in its YMIR_VERSION - set GycVersions.bootstrap_midgard for this stage" >&2 && exit 1; \
	fi

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

ARG YMIR_BOOTSTRAP_MIDGARD_VERSION

# gymir's Make-lang.in (>= 1.7.0) reads YMIR_BOOTSTRAP_MIDGARD_VERSION from the environment before
# falling back to its own YMIR_VERSION, so pin it to the runtime fetch_gcc_version actually built.
# Only passed when set: an empty environment variable still counts as defined for `?=`, so it
# would override that fallback with nothing and trip Make-lang.in's version check.
RUN env ${YMIR_BOOTSTRAP_MIDGARD_VERSION:+"YMIR_BOOTSTRAP_MIDGARD_VERSION=${YMIR_BOOTSTRAP_MIDGARD_VERSION}"} \
	make -j$(( $(nproc) - 1 ))
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

# Kept in one RUN with the install - see the note in jobs/clone_gcc/Dockerfile.
RUN apt-get update \
	&& apt-get install -y gcc-${GCC_MAJOR_VERSION} g++-${GCC_MAJOR_VERSION} flex autoconf automake libtool cmake patchelf libdwarf-dev git libgc-dev cpio

RUN mkdir gcc-bin
RUN mkdir -p gcc-bin/DEBIAN
RUN mkdir -p gcc-bin/usr/bin
RUN mkdir -p gcc-bin/usr/lib/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}
RUN mkdir -p gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}
COPY --from=build_first_deb gcc/gcc-install/usr/bin/x86_64-linux-gnu-gyc-${GCC_MAJOR_VERSION} gcc-bin/usr/bin/
COPY --from=build_first_deb gcc/gcc-install/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/ymir1 gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/ymir1

COPY --from=build_first_deb /gcc/gcc-bin.deb .
RUN dpkg -i gcc-bin.deb

# From 1.3.1 on, yruntime dropped its CMakeLists.txt and is built by gyllir from a gyllir.toml
# manifest instead (see the branches below). gyllir.deb is the *previous* stage's gyllir, already
# copied into this build context by VxxBuilder for fetch_gcc_version. Upstream's own yruntime
# Dockerfile instead downloads the exact GYLLIR_VERSION named in the checked-out yruntime's
# YMIR_VERSION, which is not necessarily a version this chain has built yet.
COPY gyllir.deb .
RUN dpkg -i gyllir.deb

ARG CACHE_BREAK=3
RUN git clone https://github.com/GNU-Ymir/yruntime.git 

WORKDIR /gcc/yruntime
RUN git fetch --all --tags
RUN git checkout "${MIDGARD_VERSION}";

# The installed archives and include dir are suffixed with a major.minor "short" version, and gyc
# only ever looks them up under the one baked into its own gycspec.o (LIBYMIDGARD_VERSION, which
# Make-lang.in threads in from the bootstrap checkout's MIDGARD_VERSION - pinned above). Which
# file on the midgard side carries that value changed with the build system, so read whichever
# one the build system actually in use reads rather than re-deriving it from the tag:
#  - CMake era (<= 1.3.0): CMakeLists.txt names them after YMIR_BOOTSTRAP_VERSION in this
#    checkout's YMIR_VERSION, i.e. after the gyc midgard is built with, not its own release.
#  - gyllir era (>= 1.3.1): yruntime's own `install` script names them after the midgard release
#    itself - read from its VERSION file up to 1.9.0, and from 1.10.0 on (VERSION is gone) from
#    gyllir.toml's top-level version, through .github/scripts/midgard-version.sh.
# The two genuinely disagree once a bootstrap trails a midgard release (midgard 1.5.0 carries
# YMIR_BOOTSTRAP_VERSION=1.4.0: short version 1.5 under the new rule, 1.4 under the old one).
RUN if [ -f .github/scripts/midgard-version.sh ]; then \
		bash .github/scripts/midgard-version.sh | cut -d. -f1,2 > /tmp/midgard_short_version; \
	elif [ -f gyllir.toml ]; then \
		tr -d '[:space:]' < VERSION | cut -d. -f1,2 > /tmp/midgard_short_version; \
	else \
		sed -nE 's/^YMIR_BOOTSTRAP_VERSION=([0-9]+\.[0-9]+).*/\1/p' YMIR_VERSION > /tmp/midgard_short_version; \
	fi
RUN test -s /tmp/midgard_short_version || (echo "could not derive MIDGARD_SHORT_VERSION from $(pwd)" >&2 && exit 1)

# Left alone a mismatch here would not fail anything, it would just produce a deb whose archives
# gyc can never find - so fail here rather than at the next stage's link step, which is where the
# missing -lgymidgard-debug_<version> would otherwise first show up.
RUN EXPECTED="$(echo "${MIDGARD_VERSION}" | cut -d. -f1,2)" \
	&& SHORT="$(cat /tmp/midgard_short_version)" \
	&& { [ "$SHORT" = "$EXPECTED" ] \
		|| (echo "midgard would install libgymidgard-*_$SHORT, but this gyc links _$EXPECTED" >&2 && exit 1) ; }

# CMake installs through DESTDIR and leaves the .yr sources to be copied by hand; the gyllir era
# ships an `install` script that does both, but writes to the real /usr, so run it and mirror
# what it produced into the package root. `gyllir build` drops the unversioned archives at the
# repo root, which `install` then renames and suffixes.
#
# Only the three library targets `install` picks up are built, one `gyllir build <target>` each,
# rather than the whole manifest: gyllir.toml also declares a `midgard_tests` executable, and
# linking that one needs an already-installed midgard (gyc appends -lgymidgard-debug_<version>
# under -funittest). Upstream's own Dockerfile gets away with `gyllir build` because its gyc comes
# from a released .deb that still bundles the previous midgard; here gyc is the one just built in
# build_first_deb, which carries no midgard at all - and the archives that would satisfy the link
# are the ones this very step is producing, not installed until `install` runs below. The deb needs
# only the libraries, so the test executable is simply not built. Target names mirror the
# `for name in debug release tests` loop in `install`.
RUN if [ -f gyllir.toml ]; then \
		for name in release debug tests; do \
			gyllir build gymidgard_$name || exit 1; \
		done; \
	else \
		mkdir .build \
			&& cd .build \
			&& touch __lib_test_.o __lib_debug_.o __lib_release_.o \
			&& cmake .. \
			&& make \
			&& make install DESTDIR=/gcc/gcc-bin; \
	fi

# `install` also sources this checkout's YMIR_VERSION for the GCC_VERSION whose libexec include
# dir it writes into. Pin it to the major this stage is actually packaging, the same way the
# bootstrap checkout's MIDGARD_VERSION is pinned in fetch_gcc_version.
RUN if [ -f gyllir.toml ]; then \
		sed -i "s/^GCC_VERSION=.*/GCC_VERSION=${GCC_VERSION}/" YMIR_VERSION \
		&& ./install \
		&& SHORT="$(cat /tmp/midgard_short_version)" \
		&& LIBEXEC="/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir" \
		&& mkdir -p /gcc/gcc-bin/usr/lib /gcc/gcc-bin/usr/include/ymir /gcc/gcc-bin$LIBEXEC \
		&& cp /usr/lib/libgymidgard-*_$SHORT.a /gcc/gcc-bin/usr/lib/ \
		&& cp -r /usr/include/ymir/$SHORT /gcc/gcc-bin/usr/include/ymir/ \
		&& cp -r $LIBEXEC/$SHORT /gcc/gcc-bin$LIBEXEC/; \
	fi

WORKDIR /gcc/yruntime/midgard

RUN if [ ! -f ../gyllir.toml ]; then \
		MIDGARD_SHORT_VERSION="$(cat /tmp/midgard_short_version)" && echo "$MIDGARD_SHORT_VERSION" \
		&& mkdir -p /gcc/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir/$MIDGARD_SHORT_VERSION \
		&& cp -r * /gcc/gcc-bin/usr/libexec/gcc/x86_64-linux-gnu/${GCC_MAJOR_VERSION}/include/ymir/$MIDGARD_SHORT_VERSION; \
	fi

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
