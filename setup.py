#!/usr/bin/env python
#
# Setup routine
#

"""
(c) 2011 Jens Kasten <jens@kasten-edv.de>
"""

from distutils.core import setup
from os.path import join, isdir
from os import listdir


files = [join("bin", i) for i in listdir("bin")]
dirs = [join("kvmtools", i) for i in listdir("kvmtools") if isdir(join("kvmtools",i))]
dirs.append("kvmtools")

setup(
    name = "kvmtools",
    version = "0.1.6.4",
    keywords = ["kvm-admin", "kvmtools"],
    author = "Jens Kasten",
    author_email = "jens@kasten-edv.de",
    description = ("Tools to manage kvm guests on commandline."),
    license = "GPL2",
    packages = dirs,
    scripts = files
)    

