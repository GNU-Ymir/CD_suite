#!/usr/bin/env python3

from utils import builder

import logging
import yaml
import time
import argparse
import subprocess

import signal
import sys



def parseArguments ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("config", help="the yamk configuration file")

    return parser.parse_args ()


def main (args) :
        bld = builder.Builder (args.config)
        bld.run ();


if __name__ == "__main__" :
    main (parseArguments ())
