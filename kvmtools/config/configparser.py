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
(c) 2007-2011 Jens Kasten <jens@kasten-edv.de>
"""

import os
import sys
import re


class Parser(object):
    """Simple config parser for kvm guest config file."""

    def __init__(self):
        # list thats contain all lines from configurations file
        self.config_lines = []
        # dictionary thats contain the configuration parameters 
        self.config = {}

    def read_config(self, config_name):
        """
        Read the file content from a guest configuration.
        Full list self.config_lines with all lines.
        @param string config_name
        """
        if not os.path.isfile(config_name):
            print "Configuration file '%s' does not exists." % config_name
            sys.exit()
        else:
            try:
                # set a line counter
                counter = 1 
                _fd = open(config_name)
                lines = _fd.readlines()
                # remove withespace but not and arguments 
                # and add them to a list
                for line in lines:
                    if len(line) > 1 and not line.startswith('#'):
                        # split only the first equal sign
                        temp = line.strip().split("=", 1)
                        # check for sign '=' 
                        if len(temp) == 1:
                            msg = "Missing sign '=' in %s on line %s" % \
                                (config_name, counter)
                            raise Exception(msg)
                        # remove all withespace from string
                        temp_first = re.sub(r'\s', '', temp[0])
                        # remove only the withspace on the beginning and the end
                        temp_second = temp[1].lstrip(' ')
                        temp_second = temp_second.split("#")[0].rstrip(" ")
                        # put the cleaned string together again
                        temp_result = "=".join([temp_first, temp_second])
                        self.config_lines.append(temp_result)
                        counter += 1
                _fd.close()
            except OSError, error_msg:
                print str(error_msg)
                sys.exit(1)

    def __call__(self, config_name):
        """Return a dictionary"""
        self.read_config(config_name)
        # counter for printing exact position if a error occur
        try:
            drive = {}
            drive_counter = 0
            net = {}
            net_counter = 0
            chardev = {}
            chardev_counter = 0
            for line in self.config_lines:
                if len(line) > 0:
                    line = line.split("=", 1)
                    # check for drive, net and char keys and 
                    # add them im a separate dict to avoid overriding
                    if line[0] == "drive":
                        drive[drive_counter] = line[1]
                        self.config['drive'] = drive
                        drive_counter += 1
                    elif line[0] == "net":
                        net[net_counter] = line[1]
                        self.config['net'] = net
                        net_counter += 1
                    elif line[0] == "chardev":
                        chardev[chardev_counter] = line[1]
                        self.config['chardev'] = chardev
                        chardev_counter += 1
                    else:
                        self.config[line[0]] = line[1]
                    if len(line[1]) == 0:
                        raise IndexError
            return self.config
        except IndexError:
            msg = "Missing value for key '%s' in %s" % (line[0], config_name)
            print msg               
            print "Use syntax: key = value"
            sys.exit()                
