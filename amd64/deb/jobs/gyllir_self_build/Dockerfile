ARG GCC_MAJOR_VERSION="15"
ARG GYLLIR_VERSION="1.2.0"
ARG GYLLIR_VERSION_NUMBER="1.2.0"
ARG ARCH="amd64"
ARG UBUNTU_VERSION="26.04"

# From 1.2.0 onward, Gyllir is no longer built with CMake: its own Dockerfile builds it with a
# previously-released gyllir binary (`gyllir build --release`), reading a gyllir.toml manifest.
# gyc.deb and gyllir.deb (the bootstrap gyllir, one major version behind) are copied in from
# results/ by GyllirSelfBuilder rather than downloaded from GitHub releases like upstream does.
FROM ubuntu:${UBUNTU_VERSION} AS install_toolchain

ARG GCC_MAJOR_VERSION

RUN mkdir /gcc
WORKDIR /gcc

RUN apt-get update
RUN apt-get install -y gcc-${GCC_MAJOR_VERSION} g++-${GCC_MAJOR_VERSION} patchelf libdwarf-dev libgc-dev git

COPY gyc.deb .
COPY gyllir.deb .
RUN dpkg -i gyc.deb
RUN dpkg -i gyllir.deb

RUN gyc --version
RUN gyllir -h || true

# gyllir's test suite shells out to `git commit`/`git config --global --get user.*`.
RUN git config --global user.email "ci@gyllir.local"
RUN git config --global user.name "Gyllir CI"

FROM install_toolchain AS build_gyllir

ARG GYLLIR_VERSION

WORKDIR /gyllir
RUN git clone https://github.com/GNU-Ymir/Gyllir.git .
RUN git fetch --all --tags
RUN git checkout "${GYLLIR_VERSION}"

RUN gyllir test --dry
RUN gyllir build --release

FROM build_gyllir AS test
RUN ./gyllir.test -sf

FROM test AS package

ARG GYLLIR_VERSION_NUMBER
ARG ARCH

RUN mkdir -p /gcc/install/usr/bin /gcc/install/etc/gyllir/res /gcc/install/etc/bash_completion.d /gcc/install/DEBIAN
RUN install -m 0755 /gyllir/gyllir /gcc/install/usr/bin/gyllir
RUN cp -r /gyllir/res/html /gyllir/res/css /gyllir/res/js /gyllir/res/ico /gcc/install/etc/gyllir/res/
RUN cp /gyllir/bash/_gyllir /gcc/install/etc/bash_completion.d/

WORKDIR /gcc/install/DEBIAN
COPY control.in /gcc/install/DEBIAN/control
RUN sed -i "s/@GYLLIR_VERSION_NUMBER@/${GYLLIR_VERSION_NUMBER}/g" /gcc/install/DEBIAN/control

WORKDIR /gcc
RUN dpkg --build install
RUN mv install.deb /gyllir_${GYLLIR_VERSION_NUMBER}_${ARCH}.deb

FROM scratch AS export

ARG GYLLIR_VERSION_NUMBER
ARG ARCH

COPY --from=package /gyllir_${GYLLIR_VERSION_NUMBER}_${ARCH}.deb /

CMD ["true"]
