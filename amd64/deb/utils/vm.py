#!/usr/bin/env python3

import os
import subprocess
from subprocess import Popen, PIPE, STDOUT

vagrant = """
Vagrant.configure("2") do |config|
  config.vm.box = "alvistack/ubuntu-24.04"
  config.ssh.forward_agent = true
  config.vm.provider "libvirt" do |v|
    v.memory = 8192
    v.cpus = 4
  end

  # Mount cachecache directories
  config.vm.provision "shell" do |s|
      s.inline = "apt-get update"
  end
end
"""

class VMLauncher :

    def __init__ (self):
        try:
            os.mkdir(".vagrant")
            print(f"Directory '{directory_name}' created successfully.")
        except Exception:
            pass

        with open (".vagrant/Vagrantfile", "w") as f:
            f.write (vagrant)

    # Boot the VM
    def boot (self) :
        p = subprocess.Popen('vagrant up', stdout = PIPE, stderr = STDOUT, shell = True, cwd="./.vagrant")
        while True:
            line = p.stdout.readline()
            if not line: break
            print (line.decode ("utf-8"), end="")

        p = subprocess.Popen('vagrant provision', stdout = PIPE, stderr = STDOUT, shell = True, cwd="./.vagrant")
        while True:
            line = p.stdout.readline()
            if not line: break
            print (line.decode ("utf-8"), end="")


    # Run a command inside the VM
    def runCmd (self, cmd) :
        p = subprocess.Popen ("vagrant ssh -- -t \'" + cmd + "\'", stdout = PIPE, stderr = STDOUT, shell = True, cwd="./.vagrant")
        while True:
            line = p.stdout.readline()
            if not line: break
            print (line.decode ("utf-8"), end="")


    # Upload file to vagrant vm
    def uploadFile (self, fr, to) :
        p = subprocess.Popen (f"vagrant scp {fr} {to}",  stdout = PIPE, stderr = STDOUT, shell = True, cwd="./.vagrant")
        while True:
            line = p.stdout.readline()
            if not line: break
            print (line.decode ("utf-8"), end="")


    # Upload file to vagrant vm
    def downloadFile (self, fr, to) :
        p = subprocess.Popen (f"vagrant scp :{fr} {to}",  stdout = PIPE, stderr = STDOUT, shell = True, cwd="./.vagrant")
        while True:
            line = p.stdout.readline()
            if not line: break
            print (line.decode ("utf-8"), end="")
