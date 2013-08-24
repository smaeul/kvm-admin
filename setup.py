#!/usr/bin/env python
#
# Setup routine
#

"""
(c) 2011-2013 Jens Kasten <jens@kasten-edv.de>

last modified: 20130823
"""

from distutils.core import setup
import os
import sys
from shutil import copytree, copy, rmtree
from subprocess import call

from kvmtools.header import Header


def copy_configs():
    path = Header()
    example = os.path.join(path.kvm_domains_dir, "example")
    if os.path.isdir(path.kvm_scripts_dir):
        rmtree(path.kvm_scripts_dir)
    copytree("scripts", path.kvm_scripts_dir)
    # make the network script executable
    for i in os.listdir(path.kvm_scripts_dir):
        if os.path.isfile(os.path.join(path.kvm_scripts_dir, i)):
            os.chmod(os.path.join(path.kvm_scripts_dir, i), 0755)
    if os.path.isdir(path.kvm_config_dir):
        rmtree(path.kvm_config_dir)
    copytree("config", path.kvm_config_dir)
    os.chmod(path.kvm_config_dir, 0755)
    if not os.path.isdir(path.kvm_domains_dir):
        os.mkdir(path.kvm_domains_dir)
    os.chmod(path.kvm_domains_dir, 0755)
    copy("domains/example", example)
    if not os.path.isdir(path.kvm_auto_dir):
        os.mkdir(path.kvm_auto_dir)
    os.chmod(path.kvm_auto_dir, 0755)

if os.getuid() != 0:
    print "Script need root user rights to install."
    print "Change user to root user or use sudo."
    sys.exit(1)

files = [os.path.join("bin", i) for i in os.listdir("bin")]
dirs = [os.path.join("kvmtools", i) for i in os.listdir("kvmtools") if os.path.isdir(os.path.join("kvmtools",i))]
dirs.append("kvmtools")

setup(
    name = "kvmtools",
    version = "0.1.7.8",
    keywords = ["kvm-admin", "kvmtools"],
    author = "Jens Kasten",
    author_email = "jens@kasten-edv.de",
    description = ("Tools to manage kvm guests on commandline."),
    license = "GPL2",
    packages = dirs,
    scripts = files
)    
copy_configs()
# generate qemu-kvm options
try:
    call(["generate-kvm-options", "-g"])
except KeyboardInterrupt:
    sys.exit(0)
