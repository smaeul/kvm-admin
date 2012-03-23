"""
(c) 2012 Jens Kasten <jens@kasten-edv.de>
"""

import os
import sys
from subprocess import Popen, PIPE

# need to import kvmtools to get absolute path
import kvmtools
from kvmtools.functions import which
from kvmtools.header import Header 
from kvmtools.config.parser import Parser


class CheckKvm(Parser, Header):

    def __init__(self):
        self.qemu_kvm_help = []
        self.qemu_kvm_options = []
        self.qemu_kvm = False
        Header.__init__(self)

    def prepare_generator(self):
        """Collect all what is need to run.
        Even if the qemu-kvm is not installed on the system.
        """
        self.get_module_path()
        if self.get_kvm_path_from_file():
            self.update_kvm_global_config()
            if not self.get_qemu_kvm_help():
                print "This is not a qemu-kvm binary."
                print "Edit %s to correct it." % self.get_abs_path_kvm_config()
                sys.exit(1)
        elif self.get_kvm_path_from_input():
            if not self.get_qemu_kvm_help():
                print "This is not a qemu-kvm binary."
                print "You have to call the command below again."
                print "Execute: generate-kvm-options -g"
                sys.exit(1)
        else:
            print "You have to update the config file manually." 
            print "You have set the correct path in for qemu-kvm in %s" % \
                self.get_abs_path_kvm_config()

    def get_abs_path_kvm_config(self):
        """Build and return the absolute path for global config."""
        kvm_config = os.path.join(self.kvm_base_config_dir, 
                                  self._kvm_conf_dir, 
                                  self._kvm_conf_name)
        if os.path.isfile(kvm_config):
            return kvm_config
        else:
            return False
    
    def get_module_path(self):
        """Get absolute path to kvmtools."""
        self.module_path = os.path.abspath(os.path.dirname(kvmtools.__file__))
        self.qemu_kvm_options_file = os.path.join(self.module_path,
                                     self.qemu_kvm_options_file_name)

    def get_kvm_path_from_file(self):
        """Try to find the absolute path.
        First from default kvm.cfg.
        If its failed then give the user the possibility 
        to give the absolute path or name to the qemu-kvm binary.
        """
        kvm_config = self.parse_config(self.get_abs_path_kvm_config())
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

    def update_kvm_global_config(self):
        """Replace the qemu-kvm default value in the global config file."""
        kvm_config = self.get_abs_path_kvm_config() 
        print "Update %s" % kvm_config
        if os.access(kvm_config, os.W_OK):
            fd = None
            try:
                fd = open(kvm_config, "r")
                lines = fd.readlines()
                new_lines = []
                for line in lines:
                    if line.lstrip().startswith("qemu-kvm"): 
                        qemu_kvm = "qemu-kvm = %s\n" % self.qemu_kvm
                        new_lines.append(qemu_kvm)
                    else:
                        new_lines.append(line)
            except IOError, e:
                print "Operation failed: %s on %s" % (e, kvm_confg)
            finally:
                if fd:
                    fd.close()
                    if len(new_lines) > 0:
                        try:
                            fd = open(kvm_config, "w")
                            for line in new_lines:
                                fd.write(line)
                        except IOError, e:
                            print "Operation failed: %s on %s" % (e, 
                                kvm_config)
                        finally:
                            if fd:
                                print "Done"
                                fd.close()
        else:
            print "No write permission to %s." % kvm_config
            sys.exit(1)

    def get_qemu_kvm_help(self):
        """This call the give qemu-kvm name
        and check if the help if in the first line the qemu name.
        This check have to be done, because it will write in the config file.
        Its return the help 
        """
        self.qemu_kvm_options = []
        process = Popen([self.qemu_kvm, "-h"], stdout=PIPE, stderr=PIPE)
        result = process.communicate()[0]
        qemu_kvm_help = result.split("\n")
        if "QEMU" in qemu_kvm_help[0]:
           self.qemu_kvm_options = qemu_kvm_help
           return True
        else:
            return False

