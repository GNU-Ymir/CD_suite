#!/usr/bin/env python3


import docker
import json
import click
import tarfile
import os
import shutil

class GyllirBuilder:

    def __init__(
            self,
            *,
            gyc: str,
            compile_with: str,
            gyllir_version: str,
            ubuntu_version: str,
    ):
        self.api = docker.APIClient()
        self.client = docker.from_env()
        self.gyc: str = gyc
        self.gyllir_version: str = gyllir_version
        self.ubuntu_version: str = ubuntu_version

        self.gcc_version = compile_with
        self.major = compile_with
        if compile_with.find (".") != -1:
            self.major = compile_with[0:compile_with.find (".")]

    def run(self):
        self.buildGyllir()
        self.retreiveDebFile()

    def buildGyllir(self):
        shutil.copy (f"results/gyc-{self.gyc}_amd64.deb", "jobs/gyllir_build/gyc.deb")
        generator = self.api.build(
            path="jobs/gyllir_build/.",          # directory containing your Dockerfile
            tag=f"gyllir:from_{self.gyllir_version}",
            buildargs={
                "GCC_VERSION": self.gcc_version,
                "GCC_MAJOR_VERSION": self.major,
                "UBUNTU_VERSION": self.ubuntu_version,
                "GYLLIR_VERSION": self.gyllir_version,
                "ARCH": "amd64"
            }
        )

        self.showLogs(generator)
        os.remove ("jobs/gyllir_build/gyc.deb")

    def retreiveDebFile(self):
        container = self.client.containers.create(
            image=f"gyllir:from_{self.gyllir_version}",
            name="extract",
            command=""   # important for scratch/minimal images
        )

        print("Created container:", container.id)

        bits, stat = container.get_archive(f"/gyllir_{self.gyllir_version}_amd64.deb")

        with open(f"results/gyllir_{self.gyllir_version}_amd64.tar", "wb") as f:
            for chunk in bits:
                f.write(chunk)

        container.remove ()

        with tarfile.open(f"results/gyllir_{self.gyllir_version}_amd64.tar") as tar:
            tar.extractall("results/")
        os.remove (f"results/gyllir_{self.gyllir_version}_amd64.tar")

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
