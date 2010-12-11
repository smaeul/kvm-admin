#!/usr/bin/env python

""" 
Parser to get content from a configfile.
(c) 2007-2010 Jens Kasten <jens@kasten-edv.de>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import os
import sys
import re


class Parser:

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
                fd = open(config_name)
                # add lines to a list and remove all withespaces 
                self.config_lines = [re.sub(r'\s', '', line) for line in fd]
                fd.close()
            except OSError, e:
                print str(e)
                sys.exit()


    def __call__(self, config_name):
        """  
        Return a dictionary
        """
        self.read_config(config_name)
        # counter for printing exact position if a error occur
        try:
            counter = 1
            drive = {}
            drive_counter = 0
            net = {}
            net_counter = 0
            chardev = {}
            chardev_counter = 0
            for line in self.config_lines:
                # remove empty lines and coments at line begin
                if len(line) > 0 and not re.search("^#", line):
                    line = line.split("=", 1)
                    # remove coments after values
                    value = line[1].split('#', 1)
                    # check for drive, net and char keys and add them im a separate dict 
                    # to avoid overriding
                    if line[0] == "drive":
                        drive[drive_counter] = value[0]
                        self.config['drive'] = drive
                        drive_counter += 1
                    elif line[0] == "net":
                        net[net_counter] = value[0]
                        self.config['net'] = net
                        net_counter += 1
                    elif line[0] == "chardev":
                        chardev[chardev_counter] = value[0]
                        self.config['chardev'] = chardev
                        chardev_counter += 1
                    else:
                        self.config[line[0]] = value[0]
                    if len(value[0]) == 0:
                        raise IndexError
                counter += 1                        
            return self.config
        except IndexError, e:
            msg = "Missing value for key '%s' on line %d in '%s'" % \
                (line[0], counter, config_name)
            print msg               
            print "Use syntax: key = value"
            sys.exit()                
                    
# vim: tabstop=4 expandtab shiftwidth=4
