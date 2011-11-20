#!/usr/bin/env python
#
# Module to generate qemu-kvm options to compare them with kvm guest config
# file to validate them.
# 

"""
(c) 2010 Jens Kasten <jens@kasten-edv.de>
"""

import os
import re
from subprocess import Popen, PIPE

# need to import kvmtools to get absolute path
import kvmtools
from kvmtools.functions import which


class Generator(object):
    """Generate qemu-kvm options and write them in file
    qemu_kvm_options.py."""

    def __init__(self):
        # binary name for qemu-kvm
        self.qemu_kvm = "kvm"
        # default setting for most parameters
        self.disabled = "disabled"
        # default setting for options_enabled_by_default
        self.enabled = "enabled"
        # file where to write the dictonary
        module_path = os.path.abspath(os.path.dirname(kvmtools.__file__))
        self.file_to_write = os.path.join(module_path, "qemu_kvm_options.py")
        # option to exclude
        self.exclude_options = ['h', 'version']
        # print output of all values of the generated dictionary
        self.verbose = False
        self.arguments()

    def arguments(self):
        """Check input and set the binary path."""
        bin_path = which(self.qemu_kvm)
        if bin_path:
            self.qemu_kvm = bin_path
            return 
        print "Type the qemu-kvm binary name and press enter or q to quit."
        while True:
            result = raw_input("Name: ")
            if result == "q":
                break
            bin_path = which(result)
            if bin_path:
                self.qemu_kvm = bin_path
                break

    def generate(self):
        """Extract all arguments."""
        try:
            # dictionary which contain all options
            output = {}
            # line counter as key for dictionary output 
            line_counter = 0
            # remove the file if its already exists
            if os.path.isfile(self.file_to_write):
                os.remove(self.file_to_write)
            if self.verbose:
                print "Path to auto generated file: %s" % self.file_to_write

            cmd = [self.qemu_kvm, '--help']
            process = Popen(cmd, stdout=PIPE, stderr=PIPE)
            process.wait()
            result = process.communicate()
            if len(result[1]) > 0:
                print result[1]
                return
            if len(result[0]) == 0:
                raise Exception("No output: %s --help" % self.file_to_write)
            status = result[0].split("\n")

            if self.verbose:
                print "Generated for: %s" % status[0]

            header = "#!/usr/bin/env python\n"
            header += '#\n'
            header += "# Autogenerated dictionary. Don't edit this file!\n#\n"
            header += '# Generated for: %s\n#\n\n' % status[0]
            header += "qemu_kvm_options = {\n"
            footer = "}\n"

            # extract option from kvm --help output
            for line in status:
                if line.startswith('-'):
                    # split options from help text
                    options = line.split(' ', 1)
                    # remove leading sign '-' and newline
                    options = options[0][1:].strip("\n")
                    # check for special line like fda/fdb or hda/hdb 
                    if re.search('/', options):
                        options_two = options.split('/')
                        output[line_counter] = '\t"%s": "%s",' % \
                            (options_two[0], self.disabled)
                        line_counter += 1
                        output[line_counter] = '\t"%s": "%s",' % \
                            (options_two[1][1:], self.disabled)
                        line_counter += 1
                    else:
                        # remove option which only display help text
                        if options not in self.exclude_options:
                            output[line_counter] = '\t"%s": "%s",' % \
                                (options, self.disabled)
                            line_counter += 1 
                               
            # write output to file
            _fd = open(self.file_to_write, 'a')
            _fd.write(header)
            for index, value in output.iteritems():
                if index == 0:
                    if self.verbose:
                        print value
                    _fd.write(value + "\n")
                else:
                    # check for double key
                    if value != output[index-1]:
                        if self.verbose:
                            print value
                        _fd.write(value + "\n")
            _fd.write(footer)                        
            _fd.close()
        except OSError, error_msg:
            print str(error_msg)
        except IOError, error_msg:
            print str(error_msg)
