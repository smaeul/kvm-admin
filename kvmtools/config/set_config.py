#
# Module to set the basics paths and files
#
#       The values come from header.py
#       This value surrounded by {}
#       self.kvm_base_config_dir = {/etc/kvm}
#       self.kvm_conf_dir = self.kvm_base_config_dir/{conf}
#       self.kvm_domain_dir = self.kvm_base_config_dir/{domains}
#       self.kvm_domain_name = sys.argv[1]
#       self.kvm_domain_file = self.kvm_domain_dir/self.kvm_domain_name
#       self.kvm_script_dir = self.kvm_base_config_dir/{scripts}
#       self.kvm_conf_file = self.kvm_conf_dir/{kvm.cfg}

"""
(c) 2011 Jens Kasten <jens@kasten-edv.de>
"""

import os

from kvmtools.header import Header


class SetConfig(Header):

    def __init__(self):
        Header.__init__(self)
        # initialize attribute
        # keep all file name which are found in dir domains
        self.kvm_domain_name_all = []
        # keep the on the fly create values
        self.kvm_domain_file = None
        self.kvm_pidfile = None
        self.kvm_socketfile = None
        self.kvm_conf_file = None
        self._value = None
        self.config()

    def config(self):
        """Methode to call from other modules. 
        Set all nesessary attribute."""
        self._set_kvm_script_dir()
        self._set_kvm_conf_dir()
        self._set_kvm_conf_file()
        self._set_kvm_domain_dir()
        self._set_kvm_domain_name_all()

    def _set_kvm_pid_file(self):
        """Set the absolute path for the pidfile."""
        kvm_pidfile = "".join([self.kvm_domain_name, ".pid"])
        self.kvm_pidfile = os.path.join(self.kvm_run_path, kvm_pidfile)
        assert type(self.kvm_pidfile) is str, "pidfile is None"
    
    def _set_kvm_socket_file(self):
        """Set the absolute path for the socketfile."""
        kvm_socketfile = "".join([self.kvm_domain_name, ".socket"])
        self.kvm_socketfile = os.path.join(self.kvm_run_path, kvm_socketfile)
        assert type(self.kvm_socketfile) is str, "socketfile is None"

    def _set_kvm_script_dir(self):
        """Set the absolute path for global configuration directory."""
        kvm_script_dir = os.path.join(self.kvm_base_config_dir,
            self._kvm_script_dir)
        if os.path.isdir(kvm_script_dir):
            self.kvm_script_dir = kvm_script_dir
        assert type(self.kvm_script_dir) is str, "kvm_script_dir is None"

    def _set_kvm_conf_dir(self):
        """Set the absolute path for global configuration directory."""
        kvm_conf_dir = os.path.join(self.kvm_base_config_dir,
            self._kvm_conf_dir)
        if os.path.isdir(kvm_conf_dir):
            self.kvm_conf_dir = kvm_conf_dir
        assert type(self.kvm_conf_dir) is str, "kvm_conf_dir is None"

    def _set_kvm_conf_file(self):
        """Set the global config file."""
        kvm_conf_file = os.path.join(self.kvm_conf_dir, self._kvm_conf_name)
        if os.path.isfile(kvm_conf_file):
            self.kvm_conf_file = kvm_conf_file
        assert type(self.kvm_conf_file) is str, "kvm_conf_file is None"

    def _set_kvm_domain_dir(self):
        """Set the absolute path for domain configuration directory."""
        kvm_domain_dir = os.path.join(self.kvm_base_config_dir,
            self._kvm_domain_dir)
        if os.path.isdir(kvm_domain_dir):
            self.kvm_domain_dir = kvm_domain_dir
        assert type(self.kvm_domain_dir) is str, "kvm_domain_dir is None"

    def _set_kvm_domain_name_all(self):
        """Set all available guests as an dictionary."""
        for domain_name in os.listdir(self.kvm_domain_dir):
            if os.path.isfile(os.path.join(self.kvm_domain_dir, domain_name)):
                self.kvm_domain_name_all.append(domain_name)

    # property to set, get, and delte the domain_conf_file
    def _set(self, value):
        """Set property."""
        if value:
            self._value = value
            self.kvm_domain_file = os.path.join(self.kvm_domain_dir, value)
            assert type(self.kvm_domain_file) is str, \
                "kvm_domain_file is None"
            self._set_kvm_pid_file()
            self._set_kvm_socket_file()
            self.build_command()
            self.get_pid()

    def _get(self):
        """Get property."""
        return self._value

    kvm_domain_name = property(_get, _set)
