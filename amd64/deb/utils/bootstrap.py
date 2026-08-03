#!/usr/bin/env python3

import docker
import json
import click
import tarfile
import os
import shutil

class VxxBuilder:
    def __init__(self, gcc_version: str, compiler_version: str, prev_gcc_version: str, prev_version: str, ymir_version: str):
        self.api = docker.APIClient()
        self.client = docker.from_env()
        self.gcc_version: str = gcc_version
        self.compiler_version: str = compiler_version
        self.prev_gcc_version: str = prev_gcc_version
        self.ymir_version: str = ymir_version
        self.prev_version: str = prev_version

        self.major = gcc_version
        if gcc_version.find (".") != -1:
            self.major = gcc_version[0:gcc_version.find (".")]

        self.compiler_major = compiler_version
        if compiler_version.find (".") != -1:
            self.compiler_major = compiler_version[0:compiler_version.find (".")]

        self.prev_major = prev_gcc_version
        if prev_gcc_version.find (".") != -1:
            self.prev_major = prev_gcc_version[0:prev_gcc_version.find (".")]

    def run(self):
        #self.createCloneImage ()
        self.buildGyc ()
        self.retreiveDebFile ()
        

    def createCloneImage(self):
        generator = self.api.build(
            path="jobs/clone_gcc/.",          # directory containing your Dockerfile
            tag="gyc:gcc_clone"            
        )

        self.showLogs(generator)        

    def buildGyc(self):
        shutil.copy (f"results/gyc-{self.prev_major}_{self.prev_version}_amd64.deb", "jobs/bootstrap_build/gyc.deb")
        shutil.copy (f"results/gyllir_{self.prev_version}_amd64.deb", "jobs/bootstrap_build/gyllir.deb")

        generator = self.api.build(
            path="jobs/bootstrap_build/",
            tag=f"gyc:final_{self.ymir_version}_deb",
            buildargs={
                "GCC_VERSION" : self.gcc_version,
                "GCC_MAJOR_VERSION" : self.major,
                "COMPILER_MAJOR_VERSION" : self.compiler_major,
                "YMIR_VERSION": self.ymir_version,
                "ARCH": "amd64"
            }
        )

        self.showLogs(generator)
        os.remove ("jobs/bootstrap_build/gyc.deb")
        os.remove ("jobs/bootstrap_build/gyllir.deb")
                
    def retreiveDebFile(self):        
        container = self.client.containers.create(
            image=f"gyc:final_{self.ymir_version}_deb",
            name="extract",
            command=""   # important for scratch/minimal images
        )
        
        print("Created container:", container.id)

        bits, stat = container.get_archive(f"/gyc-{self.major}_{self.ymir_version}_amd64.deb")

        with open(f"results/gyc-{self.major}_{self.ymir_version}_amd64.tar", "wb") as f:
            for chunk in bits:
                f.write(chunk)
                
        container.remove ()
            
        with tarfile.open(f"results/gyc-{self.major}_{self.ymir_version}_amd64.tar") as tar:
            tar.extractall("results/")
        os.remove (f"results/gyc-{self.major}_{self.ymir_version}_amd64.tar")

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
