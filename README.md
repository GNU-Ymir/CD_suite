# Description

This repository contains the scripts used to generate binaries.
__For the moment only amd64 debian binaries are targeted__, contributions would be greatly appreciated.

# AMD64 

Dependencies : 
 - vagrant
 - virtualbox / libvirt

## vagrant file

To compile the debian packages a VM has to be provisionned, this VM is defined by the Vagrantfile.
The VM compiles the different ymir project in a directory of the host machine. 

First replace the variable YMIR_HOME by the host path in the `Vagrantfile.template`, and create a `Vagrantfile`.
This is automatized by the `configure.sh` script.

```bash
./configure.sh /home/bob/ymir/
```

Then provision the VM.

```bash
cd amd64/deb/
vagrant up
```

Once the VM is up the different binaries can be created. They must be
created in the correct order, 1) gymir, 2) midgard, 3) gyllir.

## Gymir

Gymir is the compiler for the ymir language.

```bash 
cd amd64/deb/
vagrant ssh -c 'bash -s' gymir/clone.sh
vagrant ssh -c 'bash -s' gymir/configure.sh
vagrant ssh -c 'bash -s' gymir/make.sh
vagrant ssh -c 'bash -s' gymir/bin.sh
```

__Depending on your configuration vagrant vm might have a password, it is `vagrant`__
The debian binary can be found in your host directory `${YMIR_HOME}/gymir/gcc-bin/gyc-9_9.3.0_amd64.deb`

## Midgard

Midgard is the standard library of the ymir language.

```bash
cd amd64/deb/
vagrant ssh -c 'bash -s' midgard/make.sh
```

The debian binary can be found in your host directory `${YMIR_HOME}/midgard/bin/libgmidgard_9.3.0_amd64.deb`


## Gyllir

Gyllir is the package manager of ymir.

```bash
cd amd64/deb/
vagrant ssh -c 'bash -s' gyllir/make.sh
```

The debian binary can be found in your host directory `${YMIR_HOME}/gyllir/bin/gyllir_0.1.0_amd64.deb`
