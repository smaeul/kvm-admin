#
# Module to edit or create a guest configfile for kvm-admin
#

"""
(c) Jens Kasten <jens@kasten-edv.de>
"""

import os

from kvmtools.config.config import Domain
from kvmtools.system_utils import System
from kvmtools.config.create_dialog import CreateDialogConsole


class ModifyDomain(CreateDialogConsole):
    """Class for manipulating a guest config."""

    def __init__(self):
        # instance the parent class for create dialog
        CreateDialogConsole.__init__(self)
        # make system information available
        self.system = System()

    def create(self):
        """Create a minimalistic guest config file."""
        print ("Creating the domain config file: %s" % self.domain_conf_file)
        self._create_dialog_config("w")
        self.modify()

    def modify(self):
        """Edit a guest config file."""
        if os.path.isfile(self.domain_conf_file):
            if os.access(self.domain_conf_file, os.W_OK):
                os.execl("/usr/bin/editor", "", self.domain_conf_file)
            else:
                print ("Permission denied to write to %s" % \
                    self.domain_conf_file)
        else:
            self.create()

    def read(self):
        with open(self.domain_conf_file) as _fd:
            lines = _fd.readlines()
            for line in lines:
                print lines
                        
   

def main():
    domain = Domain()
    domain_name = "testme"
    domain.domain_conf_name = domain_name
    m = ModifyDomain()
    m.domain_conf_name = domain.domain_conf_name
    m.domain_conf_file = domain.domain_conf_file
    m.uuid = "1-1-1-1"
    m.create()
    #m.modify()
    m.read()

if __name__ == "__main__":
    main()

