#!/usr/bin/env python3

import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path

vagrant = """
Vagrant.configure("2") do |config|
  config.vm.box = "alvistack/ubuntu-24.04"
  config.ssh.forward_agent = true
  config.vm.provider "libvirt" do |v|
    v.memory = 8192
    v.cpus = 4
  end

  config.nfs.verify_installed = false
  config.vm.synced_folder '.', '/vagrant', disabled: true

  # Mount cachecache directories
  config.vm.provision "shell" do |s|
      s.inline = "apt-get update"
  end
end
"""

class VMLauncher :

    def __init__ (self, name):
        self._name = name

        try:
            os.mkdir(f".{self._name}")
            print(f"Directory '{directory_name}' created successfully.")
        except Exception:
            pass

        with open (f".{self._name}/Vagrantfile", "w") as f:
            f.write (vagrant)

    # Boot the VM
    def boot (self) :
        p = subprocess.Popen('vagrant up', stdout = PIPE, stderr = STDOUT, shell = True, cwd=f"./.{self._name}")
        while True:
            line = p.stdout.readline()
            if not line: break
            print (line.decode ("utf-8"), end="")

        p = subprocess.Popen('vagrant provision', stdout = PIPE, stderr = STDOUT, shell = True, cwd=f"./.{self._name}")
        while True:
            line = p.stdout.readline()
            if not line: break
            print (line.decode ("utf-8"), end="")

    # destroy the VM and all its files
    def destroy (self):
        p = subprocess.Popen('vagrant destroy -f', stdout = PIPE, stderr = STDOUT, shell = True, cwd=f"./.{self._name}")
        while True:
            line = p.stdout.readline()
            if not line: break
            print (line.decode ("utf-8"), end="")


    # Stop the VM
    def halt (self):
        p = subprocess.Popen('vagrant halt', stdout = PIPE, stderr = STDOUT, shell = True, cwd=f"./.{self._name}")
        while True:
            line = p.stdout.readline()
            if not line: break
            print (line.decode ("utf-8"), end="")

    # Run a command inside the VM
    def runCmd (self, cmd) :
        p = subprocess.Popen ("vagrant ssh -- -t \'" + cmd + "\'", stdout = PIPE, stderr = STDOUT, shell = True, cwd=f"./.{self._name}")
        while True:
            line = p.stdout.readline()
            if not line: break
            print (line.decode ("utf-8"), end="")


    # Upload file to vagrant vm
    def uploadFile (self, fr, to) :
        p = subprocess.Popen (f"vagrant scp {fr} {to}",  stdout = PIPE, stderr = STDOUT, shell = True, cwd=f"./.{self._name}")
        while True:
            line = p.stdout.readline()
            if not line: break
            print (line.decode ("utf-8"), end="")


    # Upload file to vagrant vm
    def downloadFile (self, fr, to) :

        try :
            path = Path(to)
            os.mkdir (path.parent.absolute())
        except Exception:
            pass

        p = subprocess.Popen (f"vagrant scp :{fr} {to}",  stdout = PIPE, stderr = STDOUT, shell = True, cwd=f"./.{self._name}")
        while True:
            line = p.stdout.readline()
            if not line: break
            print (line.decode ("utf-8"), end="")
