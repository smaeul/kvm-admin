#
# Module to set the absolute paths for domain_name 
# pidfile and socketfile
# 
#

"""
(c) 2011-2012 Jens Kasten <jens@kasten-edv.de>
"""

import os

from kvmtools.header import Header
from kvmtools.config.build_config import BuildConfig
from kvmtools.config.build_command import BuildCommand


class KvmConfig(Header, BuildConfig, BuildCommand):
    """Set when the kvm_domain_name get assigned a value 
    the pidfile and socketfile otherwise set kvm_domain_names 
    as a list with all files wich found in domains directory.
    """

    def __init__(self):
        Header.__init__(self)
        BuildConfig.__init__(self)
        BuildCommand.__init__(self)
        self.kvm_domain_names = []
        self.kvm_domain_file = None
        self.kvm_pidfile = None
        self.kvm_socketfile = None
        self._value = None

    def _set(self, value):
        """Property to set kvm_domain_file and based on this
        the pidfile and socketfile.
        """
        assert type(value) is str, "kvm_domain_name is not a string"
        self._value = value
        self.kvm_domain_file = os.path.join(self.kvm_domains_dir, value)
        kvm_pidfile = "".join([self.kvm_domain_name, ".pid"])
        self.kvm_pidfile = os.path.join(self.kvm_run_dir, kvm_pidfile)
        kvm_socketfile = "".join([self.kvm_domain_name, ".socket"])
        self.kvm_socketfile = os.path.join(self.kvm_run_dir, kvm_socketfile)
        # load config and build command, its depends on kvm_domain_name
        self.build_config()
        self.build_command()
        # call get_pid() from module system
        self.get_pid()

    def _get(self):
        """Property to get the kvm_domain_name."""
        return self._value

    kvm_domain_name = property(_get, _set)


if __name__ == "__main__":
    import sys
    conf = KvmConfig()
    if len(sys.argv) > 1:
        conf.kvm_domain_name = sys.argv[1]
    print "kvm_domain_name:", conf.kvm_domain_name
    print "kvm_pidfile:", conf.kvm_pidfile
    print "kvm_socketfile:", conf.kvm_socketfile
    print "kvm_domain_names:", conf.kvm_domain_names
    print "*" * 80
    print "call build_config()"
    conf.build_config()
    print "cleaned config dictionary"
    print conf.config
    print "*" * 80
    print "call build_command()"
    conf.build_command()
    print "print command as list:"
    print conf.command[0]
    print "print command as string:"
    print conf.command[1]
