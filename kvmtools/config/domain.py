# 
# Module which handle the domain config
#

"""
(c) 2011 Jens Kasten <jens@kasten-edv.de>
"""

import os

from kvmtools.config.set_config import SetConfig
from kvmtools.config.create_dialog import CreateDialogConsole
from kvmtools.kvm.build_command import BuildCommand
from kvmtools.kvm.monitor import Monitor
from kvmtools.kvm.system import System


class Domain(SetConfig, CreateDialogConsole, BuildCommand, Monitor, System):
    """Class domain handle the domain(guest) configuration."""

    def __init__(self):
        SetConfig.__init__(self)
        CreateDialogConsole.__init__(self)
        BuildCommand.__init__(self)
        Monitor.__init__(self)
        System.__init__(self)

    def create(self):
        """Create a minimalistic guest config file."""
        print ("Creating the domain config file: %s" % self.kvm_domain_file)
        self.create_dialog("w")
        self.modify()

    def modify(self):
        """Edit a guest config file."""
        if os.path.isfile(self.kvm_domain_file):
            if os.access(self.kvm_domain_file, os.W_OK):
                os.execl("/usr/bin/editor", "", self.kvm_domain_file)
            else:
                print ("Permission denied to write to %s" % \
                    self.kvm_domain_file)
        else:
            self.create()

