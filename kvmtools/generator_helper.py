# 
#  Helper Module to do some checks.
#

"""
(c) 2012 Jens Kasten <jens@kasten-edv.de>
"""

import os
import sys
from subprocess import Popen, PIPE

from kvmtools.functions import which
from kvmtools.header import Header
from kvmtools.config.kvm_parser import Parser


class GeneratorHelper(Header):

    def __init__(self):
        Header.__init__(self)
        self.kvm_help = []
        self.kvm_options = []
        self.qemu_kvm = False

    def prepare_generator(self):
        """Collect all what is need to run.
        Even if the qemu-kvm is not installed on the system.
        """
        if self.get_kvm_path_from_file():
            if not self.get_kvm_help():
                print "This is not a qemu-kvm binary."
                print "Edit %s to correct it." % self.kvm_config_file
                sys.exit(1)
            else:
                self.update_kvm_conf()
        elif self.get_kvm_path_from_input():
            if not self.get_kvm_help():
                print "This is not a qemu-kvm binary."
                print "You have to call the command below again."
                print "Execute: generate-kvm-options -g"
                sys.exit(1)
            else:
                self.update_kvm_conf()
        else:
            print "You have to update the config file manually." 
            print "You have set the correct path for qemu-kvm in %s" % \
                self.kvm_config_file
            sys.exit(1)
    
   
    def get_kvm_path_from_file(self):
        """Try to find the absolute path for key "qemu-kvm" value 
        in kvm_config_file.
        """
        kvm_config = Parser().parse_config(self.kvm_config_file)
        if "qemu-kvm" in kvm_config:
            kvm_name = kvm_config["qemu-kvm"]
            for i in kvm_name.split(","):
                self.qemu_kvm = which(i.strip())
                if self.qemu_kvm:
                    return True

    def get_kvm_path_from_input(self):
        """Try with the user input to set the absolute path."""
        print "Enter the qemu-kvm binary name or absolute path."
        print "When done press enter or just q to quit."
        while True:
            result = raw_input("Name: ")
            if result == "q":
                break 
            elif len(result) == 0:
                continue
            else:
                self.qemu_kvm = which(result)
                if self.qemu_kvm:
                    return True
                else:
                    print "Could not found '%s' in your PATH" % result

    def update_kvm_conf(self):
        """Replace the qemu-kvm default value in the global config file."""
        print "Update %s" % self.kvm_config_file
        if os.access(self.kvm_config_file, os.W_OK):
            fd = None
            try:
                fd = open(self.kvm_config_file, "r")
                lines = fd.readlines()
                new_lines = []
                for line in lines:
                    if line.lstrip().startswith("qemu-kvm"): 
                        qemu_kvm = "qemu-kvm = %s\n" % self.qemu_kvm
                        new_lines.append(qemu_kvm)
                    else:
                        new_lines.append(line)
            except IOError, e:
                print "Operation failed: %s on %s" % (e, self.kvm_confg_file)
            finally:
                if fd:
                    fd.close()
                    if len(new_lines) > 0:
                        try:
                            fd = open(self.kvm_config_file, "w")
                            for line in new_lines:
                                fd.write(line)
                        except IOError, e:
                            print "Operation failed: %s on %s" % (e, 
                                self.kvm_config_file)
                        finally:
                            if fd:
                                print "Done"
                                fd.close()
        else:
            print "No write permission to %s." % self.kvm_config_file
            sys.exit(1)

    def get_kvm_help(self):
        """This call the give qemu-kvm name
        and check if the help if in the first line the qemu name.
        This check have to be done, because it will write in the config file.
        Its return the help 
        """
        self.kvm_options = []
        process = Popen([self.qemu_kvm, "-h"], stdout=PIPE, stderr=PIPE)
        result = process.communicate()[0]
        kvm_help = result.split("\n")
        if "QEMU" in kvm_help[0]:
           self.kvm_options = kvm_help
           return True
        else:
            return False
        

    def check_qemu_kvm_path(self):
        """The qemu-kvm is not a valid parameter.
        This can have a single value or comma separated values.
        """
        config = Parser().parse_config(self.kvm_config_file)
        print config
        if "qemu-kvm" not in config:
            print "Copy this example:"
            print "\tqemu-kvm = qemu-kvm, kvm"
            sys.exit(1)
        else:
            if not self.check_qemu_kvm_options_file():
                self.prepare_generator()

