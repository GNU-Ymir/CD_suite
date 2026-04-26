#!/usr/bin/env python3


import docker
import json
import click
import tarfile
import os
import shutil

class GyllirBuilder:

    def __init__(self, gcc_version: str, ymir_version: str):
        self.api = docker.APIClient()
        self.client = docker.from_env()
        self.gcc_version: str = gcc_version
        self.ymir_version: str = ymir_version
                
        self.major = gcc_version
        if gcc_version.find (".") != -1:
            self.major = gcc_version[0:gcc_version.find (".")]

    def run(self):
        self.buildGyllir()
        self.retreiveDebFile()

    def buildGyllir(self):
        shutil.copy (f"results/gyc-{self.major}_{self.ymir_version}_amd64.deb", "jobs/gyllir_build/gyc.deb")
        generator = self.api.build(
            path="jobs/gyllir_build/.",          # directory containing your Dockerfile
            tag=f"gyllir:from_{self.ymir_version}",
            buildargs={
                "GCC_VERSION": self.gcc_version,
                "GCC_MAJOR_VERSION": self.major,
                "YMIR_VERSION": self.ymir_version,
                "ARCH": "amd64"
            }
        )        
        
        self.showLogs(generator)
        os.remove ("jobs/gyllir_build/gyc.deb")

    def retreiveDebFile(self):        
        container = self.client.containers.create(
            image=f"gyllir:from_{self.ymir_version}",            
            name="extract",
            command=""   # important for scratch/minimal images
        )
        
        print("Created container:", container.id)

        bits, stat = container.get_archive(f"/gyllir_{self.ymir_version}_amd64.deb")

        with open(f"results/gyllir_{self.ymir_version}_amd64.tar", "wb") as f:
            for chunk in bits:
                f.write(chunk)
                
        container.remove ()
            
        with tarfile.open(f"results/gyllir_{self.ymir_version}_amd64.tar") as tar:
            tar.extractall("results/")
        os.remove (f"results/gyllir_{self.ymir_version}_amd64.tar")        

    def showLogs(self, generator):
        while True:
            try:
                output = generator.__next__()                                    
                json_output = json.loads(output)
                if 'stream' in json_output:
                    click.echo(json_output['stream'].strip('\n'))
            except StopIteration as r:                
                click.echo("Docker image build complete.")
                break
            except ValueError:
                click.echo("Error parsing output from docker image build: %s" % output)

