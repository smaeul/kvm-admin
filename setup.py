#!/usr/bin/env python

import os
import sys
import time
from distutils.errors import DistutilsFileError
from distutils.core import setup
from distutils.file_util import copy_file
from distutils.dir_util import copy_tree
from distutils import log


def copy_files():
    kvm_config_path = "/etc/kvm"
    scripts = "scripts"
    config = "config"
    bins = "bin"
    kvm_auto = "auto"
    domains = "domains"
    example = "/".join([domains, "example"])
    var_run_kvm = "/var/run/kvm"
    kvm_user = "kvm"
    try:
        copy_tree(scripts, os.path.join(kvm_config_path, scripts))
        copy_tree(config, os.path.join(kvm_config_path, config))
        copy_tree(bins, os.path.join(sys.prefix, bins))
        copy_tree(domains, os.path.join(kvm_config_path, domains))
        copy_file(example, os.path.join(kvm_config_path, example))
        copy_tree(kvm_auto, os.path.join(kvm_config_path, kvm_auto))
        if not os.path.isdir(var_run_kvm):
            os.makedirs(var_run_kvm)
            os.chmod(var_run_kvm, 0750)
            os.chown(var_run_kvm, kvm_user, kvm_user)
    except DistutilsFileError, e:
        print e
        sys.exit()
    except OSError, e:
        print e[1]
        sys.exit()

setup(
    name = "kvm-tools",
    version = "0.1.6",
    author = "Jens Kasten",
    author_email = "jens@kasten-edv.de",
    description = ("Tool for managing kvm guests on commandline."),
    packages = ["kvmtools", ],
        
    classifiers = [
        "Development Status :: 3 - Beta",
        "Topic :: Utilities",
        "License :: GPL3",
    ],
)    
copy_files()

