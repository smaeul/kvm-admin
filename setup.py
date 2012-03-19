#!/usr/bin/env python
#
# Setup routine
#

"""
(c) 2011 Jens Kasten <jens@kasten-edv.de>
"""


from distutils.core import setup
from os.path import join, isdir, isfile
from os import listdir, mkdir, chmod
from shutil import copytree, copy, rmtree
from subprocess import call

from kvmtools.header import Header

def copy_configs():
    header = Header()
    base_dir = header.kvm_base_config_dir
    scripts = join(base_dir, header._kvm_script_dir)
    configs = join(base_dir, header._kvm_conf_dir)
    domains = join(base_dir, header._kvm_domain_dir)
    example = join(domains, "example")
    auto = join(base_dir, "auto")
    if isdir(scripts):
        rmtree(scripts)
    copytree("scripts", scripts)
    # make the network script executable
    for i in listdir(scripts):
        if isfile(join(scripts, i)):
            chmod(join(scripts, i), 0755)
    if isdir(configs):
        rmtree(configs)
    copytree("config", configs)
    if not isdir(domains):
        mkdir(domains)
    copy("domains/example", example)
    if not isdir(auto):
        mkdir(auto)


files = [join("bin", i) for i in listdir("bin")]
dirs = [join("kvmtools", i) for i in listdir("kvmtools") if isdir(join("kvmtools",i))]
dirs.append("kvmtools")

setup(
    name = "kvmtools",
    version = "0.1.7.3",
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
call(["generate-kvm-options", "-g"])
