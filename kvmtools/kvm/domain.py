# 
# Module which handle the domain configuration.
# Its uses to collect information from different modules.
# The loaded module just keep the code in different placed 
# for better maintance.
#

"""
(c) 2011-2012 Jens Kasten <jens@kasten-edv.de>
"""

import os

from kvmtools.config.kvm_config import KvmConfig
from kvmtools.kvm.create_dialog import CreateDialogConsole
from kvmtools.kvm.monitor import Monitor
from kvmtools.kvm.system import System


class Domain(KvmConfig,  Monitor, System, CreateDialogConsole):
    """Class domain handle the domain(guest) configuration."""

    def __init__(self):
        KvmConfig.__init__(self)
        Monitor.__init__(self)
        System.__init__(self)
        CreateDialogConsole.__init__(self)


    def available_domains(self):
        """Fill up the kvm_domain_names list"""
        for domain_name in os.listdir(self.kvm_domains_dir):
            # only add files
            if os.path.isfile(os.path.join(self.kvm_domains_dir, domain_name)):
                # exclude backup files
                for i in self.exclude_backup_files:
                   if not domain_name.endswith(i):
                        self.kvm_domain_names.append(domain_name)
        return self.kvm_domain_names
    
    def create(self):
        """Create a minimalistic domain config file."""
        print "Creating the domain config file: %s" % self.kvm_domain_file
        self.create_dialog()
        self.modify()

    def modify(self):
        """Edit a domain config file."""
        # TODO: check on different distribution and find a better way
        if os.path.isfile(self.kvm_domain_file):
            if os.access(self.kvm_domain_file, os.W_OK):
                try:
                    # for debian 
                    os.execl("/usr/bin/editor", "", self.kvm_domain_file)
                except OSError, e:
                    editor = os.environ["EDITOR"]
                    try:
                        # for gentoo
                        os.execl(editor, "", self.kvm_domain_file)
                    except OSError, e:
                        try:
                            # for unknown 
                            os.execl("/usr/bin/vi", "", self.kvm_domain_file)
                        except:
                            print "Operation failed: Editor is not set correct."
            else:
                print "Permission denied: No write access for %s." % \
                    self.kvm_domain_file
        else:
            self.create()

