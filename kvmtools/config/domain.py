# 
# Module which handle the domain configuration.
# Its uses to collect information from different modules.
#

"""
(c) 2011-2012 Jens Kasten <jens@kasten-edv.de>
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

