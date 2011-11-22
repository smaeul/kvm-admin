#
# Module BuildConfig collect all data to create a command qemu-kvm command.
# 

"""
(c) 2011 Jens Kasten <jens@kasten-edv.de>
"""

import os
import random
import string

from kvmtools.config.configparser import Parser
from kvmtools.kvm.validate_config import ValidateConfig


class BuildConfig(ValidateConfig):
    
    def __init__(self):
        ValidateConfig.__init__(self)
        self.config = {}
        self.monitor_options = {}
               
    def build_config(self):
        """Load domain and global config and then merge them."""
        parser = Parser()
        kvm_conf_file = parser(self.kvm_conf_file)
        self.check_config(kvm_conf_file)
        kvm_domain_file = parser(self.kvm_domain_file)
        self.check_config(kvm_domain_file)
        self._merge_configs(kvm_conf_file, kvm_domain_file)
        self._add_name()
        self._add_uuid()
        self._add_pidfile()
        self._add_monitor()
        self._check_net_tap()

    def _merge_configs(self, kvm_conf_file, kvm_domain_file):
        """Merge global and guest configfile.
        Keep this method, maybe add some more configuration files later.
        """
        for key, value in kvm_conf_file.iteritems():
            self.config[key] = value
        for key in kvm_conf_file.keys():
            if key not in kvm_conf_file:
                self.config[key] = kvm_conf_file[key]

    def _add_pidfile(self):
        """Append the pidfile option to the config dictionary or reverse."""
        if "pidfile" not in self.config:
            pidfile = os.path.join(self.kvm_run_path, self.kvm_pidfile)
            self.config["pidfile"] = pidfile
        else:
            self.kvm_pidfile = self.config["pidfile"]

    def _add_uuid(self):
        """Append an unique uuid to the config dictionary."""
        random.seed(os.urandom(8))
        charset = string.digits + "abcdef"
        eight = "".join(random.sample(charset, 8))
        four_first = "".join(random.sample(charset, 4))
        four_second = "".join(random.sample(charset, 4))
        four_third = "".join(random.sample(charset, 4))
        twelve =  "".join(random.sample(charset, 12))
        uuid = "-".join([eight, four_first, four_second, four_third, twelve])
        self.config["uuid"] = uuid

    def _add_name(self):
        """Append a name for window title and process name (on linux only)."""
        if "name" in self.config:
            name = self.config["name"].split(" ")[0]
            process_name = "=kvm_".join(["process", name])
            self.config["name"] = ",".join([name, process_name])
        else:
            process_name = "=".join(["process", self.kvm_domain_name])
            self.config["name"] = ",".join([self.kvm_domain_name, process_name])

    def _add_monitor(self):
        """Add a dictionry with type and the path to the socket file or
        the host and port.
        """
        if "monitor" in self.config:
            monitor = self.config["monitor"]
            # get the string befor the first comma 
            # and then split this string by colon
            monitor_type = monitor.split(',')[0].split(':')
            if len(monitor_type) == 3:
                # this is usally for tcp
                self.monitor_options['Type'] = monitor_type[0] 
                self.monitor_options['Host'] = monitor_type[1]
                self.monitor_options['Port'] = int(monitor_type[2])
            elif len(monitor_type) == 2:
                # this is for telnet, when no port is given
                self.monitor_options['Type'] = monitor_type[0]
                if monitor_type[0] == 'unix':
                    self.monitor_options['SocketFile'] = monitor_type[1]
                self.monitor_options['Host'] = monitor_type[1]
                self.monitor_options['Port'] = self.telnet_port
        else:
            # set unix socket as default monitor access
            monitor = "unix:%s,server,nowait" % self.kvm_socketfile
            self.monitor_options["Type"] = "unix"
            self.monitor_options['SocketFile'] = self.kvm_socketfile
        self.config["monitor"] = monitor 


