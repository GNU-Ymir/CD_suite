ARG GCC_VERSION="15"
ARG GCC_MAJOR_VERSION="15"
ARG GYLLIR_VERSION="cxx"
ARG GYLLIR_VERSION_NUMBER="0.1.0"
ARG ARCH="amd64"
ARG UBUNTU_VERSION="26.04"

FROM ubuntu:${UBUNTU_VERSION} AS install_gyc

ARG GCC_VERSION
ARG GYLLIR_VERSION
ARG GCC_MAJOR_VERSION

RUN mkdir /gcc
RUN mkdir /gcc/install

WORKDIR /gcc

RUN apt-get update
RUN apt-get install -y cmake gcc-${GCC_MAJOR_VERSION} g++-${GCC_MAJOR_VERSION} libtool cmake patchelf libdwarf-dev git libgc-dev

COPY gyc.deb .
RUN dpkg -i gyc.deb

RUN gyc --version

FROM install_gyc AS build_gyllir

ARG GCC_VERSION
ARG GYLLIR_VERSION
ARG GCC_MAJOR_VERSION

ARG BREAK=0
WORKDIR /gcc
RUN git clone https://github.com/GNU-Ymir/Gyllir.git gyllir

WORKDIR /gcc/gyllir
RUN git fetch --all --tags
RUN git checkout "${GYLLIR_VERSION}";

RUN mkdir .build

WORKDIR /gcc/gyllir/.build
RUN cmake ..
RUN make install DESTDIR=/gcc/install

WORKDIR /gcc/install
RUN mkdir -p /gcc/install/etc/bash_completion.d
RUN mkdir -p /gcc/install/usr/bin
RUN mkdir -p /gcc/install/DEBIAN
RUN cp /gcc/gyllir/bash/_gyllir /gcc/install/etc/bash_completion.d/
RUN cp /gcc/gyllir/.build/gyllir /gcc/install/usr/bin/
RUN chmod +x /gcc/install/usr/bin/gyllir

ARG GYLLIR_VERSION_NUMBER
WORKDIR /gcc/install/DEBIAN
COPY control.in /gcc/install/DEBIAN/control
RUN sed -i "s/@GCC_MAJOR_VERSION@/${GCC_MAJOR_VERSION}/g" /gcc/install/DEBIAN/control
RUN sed -i "s/@GCC_VERSION@/${GCC_VERSION}/g" /gcc/install/DEBIAN/control
RUN sed -i "s/@GYLLIR_VERSION_NUMBER@/${GYLLIR_VERSION_NUMBER}/g" /gcc/install/DEBIAN/control

ARG ARCH
WORKDIR /gcc
RUN dpkg --build install
RUN mv install.deb /gyllir_${GYLLIR_VERSION}_${ARCH}.deb

FROM scratch AS export

ARG GYLLIR_VERSION
ARG ARCH

COPY --from=build_gyllir /gyllir_${GYLLIR_VERSION}_${ARCH}.deb /

CMD ["true"]
