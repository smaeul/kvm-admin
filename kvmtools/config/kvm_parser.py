#!/usr/bin/env python
#
# Parser to get content from a configfile.
#
# config file syntax:
#       key = value
#       #key = value    <- commented 
#       key = value  # comment
#

"""
(c) 2007-2012 Jens Kasten <jens@kasten-edv.de>
"""

import os
import sys
import re

IS_QEMU_KVM_OPTION = False
try:
    from kvmtools.kvm_options import kvm_options
    IS_QEMU_KVM_OPTION = True
except ImportError, e:
    kvm_options = {}
from kvmtools.header import Header

class Parser(object):
    """Simple config parser for kvm guest config file."""
    
    def _check_config_syntax(self, config_file):
        """Return a dictionary from given config file."""
        assert type(config_file) is str, "No config file is set"
        if not os.path.isfile(config_file):
            #print "Configfile does not exist: %s" % config_file
            return False 
        else:
            counter = 1
            config = []
            fd = None
            try:
                fd = open(config_file)
                lines = fd.readlines()
                # remove withespace but not and arguments 
                for line in lines:
                    if len(line) > 1 and not line.startswith('#'):
                        # split only the first equal sign form left side
                        temp = line.strip().split("=", 1)
                        # check for sign '=' 
                        if len(temp) == 1:
                            msg = "Missing sign '=' in %s on line %s" % \
                                (config_file, counter)
                            raise RuntimeError(msg)
                        # remove all withespace from string
                        key = re.sub(r'\s', '', temp[0])
                        if IS_QEMU_KVM_OPTION:
                            if key not in Header().exclude_options \
                                and key not in kvm_options:
                                print "Not a qemu-kvm command: '%s' in %s on line %s" % \
                                     (key, config_file, counter)
                                #sys.exit(1)
                        # remove comments
                        if len(temp) == 1:
                            msg = "Missing value in %s on line %s" % \
                                (config_file, counter)
                            raise RuntimeError(msg)
                        else:
                            value = temp[1].split("#")[0].strip()
                        content = "=".join([key, value])
                        config.append(content)
                    counter += 1
            finally:
                if fd:
                    fd.close()
            return config

    def parse_config(self, config_file):
        """Return a dictionary"""
        lines = self._check_config_syntax(config_file)
        if not lines:
            return False
        config = {}
        device = {}
        device_counter = 0
        drive = {}
        drive_counter = 0
        net = {}
        net_counter = 0
        chardev = {}
        chardev_counter = 0
        for line in lines:
            if len(line) > 0:
                line = line.split("=", 1)
                # check for device, drive, net and char keys and
                # add them im a separate dict to avoid overriding
                if line[0] == "device":
                    device[device_counter] = line[1]
                    config['device'] = device
                    device_counter += 1
                elif line[0] == "drive":
                    drive[drive_counter] = line[1]
                    config['drive'] = drive
                    drive_counter += 1
                elif line[0] == "net":
                    net[net_counter] = line[1]
                    config['net'] = net
                    net_counter += 1
                elif line[0] == "chardev":
                    chardev[chardev_counter] = line[1]
                    config['chardev'] = chardev
                    chardev_counter += 1
                else:
                    config[line[0]] = line[1]
        return config

    def merge_configs(self, config_one, config_two):
        """Merge two configs into a single one without duplications."""
        config = {}
        if not config_one and not config_two:
            return {}
        if config_one and not config_two:
            return config_one
        if not config_one and config_two:
            return config_two
        for key, value in config_one.iteritems():
            config[key] = value
        for key in config_two.keys():
            if key not in config_one:
                config[key] = config_two[key]
        return config
