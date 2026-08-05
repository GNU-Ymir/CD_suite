#!/usr/bin/env python3

import docker
import json
import click
import tarfile
import os
import shutil

from utils.versions import GycVersions

class VxxBuilder:
    def __init__(
            self,
            *,
            prev_gyc: str,
            prev_gyllir: str,
            versions: GycVersions,
            ubuntu_version: str,
    ):
        self.api = docker.APIClient()
        self.client = docker.from_env()
        self.prev_gyc: str = prev_gyc
        self.prev_gyllir: str = prev_gyllir
        self.versions: GycVersions = versions
        self.ubuntu_version: str = ubuntu_version

        self.ymir_version = versions.ymir
        self.gcc_version = versions.target
        self.major = versions.target_major
        self.compiler_major = versions.compiler_major

        self.clone_image = f"gyc:gcc_clone_{ubuntu_version}"

    def run(self):
        self.createCloneImage ()
        self.buildGyc ()
        self.retreiveDebFile ()


    def createCloneImage(self):
        generator = self.api.build(
            path="jobs/clone_gcc/.",          # directory containing your Dockerfile
            tag=self.clone_image,
            buildargs={
                "UBUNTU_VERSION" : self.ubuntu_version
            }
        )

        self.showLogs(generator)

    def buildGyc(self):
        shutil.copy (f"results/gyc-{self.prev_gyc}_amd64.deb", "jobs/bootstrap_build/gyc.deb")
        shutil.copy (f"results/gyllir_{self.prev_gyllir}_amd64.deb", "jobs/bootstrap_build/gyllir.deb")

        generator = self.api.build(
            path="jobs/bootstrap_build/",
            tag=f"gyc:final_{self.versions.bootstrap}_deb",
            buildargs={
                "GCC_VERSION" : self.gcc_version,
                "GCC_MAJOR_VERSION" : self.major,
                "COMPILER_MAJOR_VERSION" : self.compiler_major,
                "CLONE_IMAGE" : self.clone_image,
                "UBUNTU_VERSION" : self.ubuntu_version,
                "GYC_VERSION": self.ymir_version,
                "YMIR_VERSION": self.versions.bootstrap,
                "MIDGARD_VERSION": self.versions.midgard,
                "ARCH": "amd64"
            }
        )

        self.showLogs(generator)
        os.remove ("jobs/bootstrap_build/gyc.deb")
        os.remove ("jobs/bootstrap_build/gyllir.deb")

    def retreiveDebFile(self):
        container = self.client.containers.create(
            image=f"gyc:final_{self.versions.bootstrap}_deb",
            name=f"extract-{self.versions.bootstrap}",
            command=""   # important for scratch/minimal images
        )

        print("Created container:", container.id)

        bits, stat = container.get_archive(f"/gyc-{self.major}_{self.versions.bootstrap}_amd64.deb")

        with open(f"results/gyc-{self.major}_{self.versions.bootstrap}_amd64.tar", "wb") as f:
            for chunk in bits:
                f.write(chunk)

        container.remove ()

        with tarfile.open(f"results/gyc-{self.major}_{self.versions.bootstrap}_amd64.tar") as tar:
            tar.extractall("results/")
        os.remove (f"results/gyc-{self.major}_{self.versions.bootstrap}_amd64.tar")

    def showLogs(self, generator):
        while True:
            try:
                output = generator.__next__()
                json_output = json.loads(output)
                if 'stream' in json_output:
                    click.echo(json_output['stream'].strip('\n'))
            except StopIteration:
                click.echo("Docker image build complete.")
                break
            except ValueError:
                click.echo("Error parsing output from docker image build: %s" % output)
