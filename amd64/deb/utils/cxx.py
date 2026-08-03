#!/usr/bin/env python3

import docker
import json
import click
import tarfile
import os

class CxxBuilder:
    def __init__(self, gcc_version: str, compiler_version: str):
        self.api = docker.APIClient()
        self.client = docker.from_env()
        self.gcc_version: str = gcc_version
        self.compiler_version: str = compiler_version

        self.major = gcc_version
        if gcc_version.find (".") != -1:
            self.major = gcc_version[0:gcc_version.find (".")]

        self.compiler_major = compiler_version
        if compiler_version.find (".") != -1:
            self.compiler_major = compiler_version[0:compiler_version.find (".")]

    def run(self):
        self.createCloneImage ()
        self.buildGyc ()
        self.retreiveDebFile ()
        

    def createCloneImage(self):
        generator = self.api.build(
            path="jobs/clone_gcc/.",          # directory containing your Dockerfile
            tag="gyc:gcc_clone"            
        )

        self.showLogs(generator)        

    def buildGyc(self):
        
        generator = self.api.build(
            path="jobs/cxx_build/",          
            tag="gyc:final_cxx_deb",
            buildargs={
                "GCC_VERSION" : self.gcc_version,
                "GCC_MAJOR_VERSION" : self.major,
                "COMPILER_MAJOR_VERSION" : self.compiler_major,
                "YMIR_VERSION": "cxx",
                "ARCH": "amd64"
            }
        )

        self.showLogs(generator)        
                
    def retreiveDebFile(self):        
        container = self.client.containers.create(
            image="gyc:final_cxx_deb",
            name="extract",
            command=""   # important for scratch/minimal images
        )
        
        print("Created container:", container.id)

        bits, stat = container.get_archive(f"/gyc-{self.major}_cxx_amd64.deb")

        with open(f"results/gyc-{self.major}_cxx_amd64.tar", "wb") as f:
            for chunk in bits:
                f.write(chunk)
                
        container.remove ()
            
        with tarfile.open(f"results/gyc-{self.major}_cxx_amd64.tar") as tar:
            tar.extractall("results/")
        os.remove (f"results/gyc-{self.major}_cxx_amd64.tar")

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
