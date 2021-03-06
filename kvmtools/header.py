#
# Kvm header file does collect all paths and stuff.
#

"""
(C) 2011-2012 Jens Kasten <jens@kasten-edv.de>
"""

import os

# need to get the absolute path
import kvmtools


class Header(object):
    """Contain all attribute to store filename or paths and some other stuff.
    """ 

    def __init__(self):
        self.kvm_errors = []
        #########
        # Paths #
        #########
        # base direcotry for configs, and scripts, and domain configs
        self.kvm_base_dir = "/etc/kvm"
        # directory name to store the ifdown and ifup scripts
        self.kvm_scripts_dir = os.path.join(self.kvm_base_dir, 'scripts')
        # directory name to store the domain configuration files
        self.kvm_domains_dir = os.path.join(self.kvm_base_dir, 'domains')
        # directory name to store the global configuration file
        self.kvm_config_dir = os.path.join(self.kvm_base_dir, 'config')
        # directory for auto start kvm domain
        # TODO: not implement 
        self.kvm_auto_dir = os.path.join(self.kvm_base_dir, "auto")
        # name for global configuration file
        self.kvm_config_name = 'kvm.cfg'
        # the absolute path for kvm_conf_file
        self.kvm_config_file = os.path.join(self.kvm_config_dir,
                                            self.kvm_config_name)
        # directory for pidfiles and socketfiles
        self.kvm_run_dir = '/var/run/kvm'
        # module path, it can placed on different directories
        # so use the imported kvmtools to get the absolute path
        self.module_path = os.path.abspath(os.path.dirname(kvmtools.__file__))
        # file name for kvm options, this file is an autogenerated
        self.kvm_options_file_name = "kvm_options.py"
        # absolute path
        self.kvm_options_file = os.path.join(self.module_path, 
                                             self.kvm_options_file_name)
        # search path's
        self.search_paths = ["/bin", "/sbin", 
                             "/usr/bin", "/usr/sbin", 
                             "/usr/local/sbin", "/usr/local/bin"]
        ###########
        # Options #
        ###########
        # default telnet port 23, can only use once at time in one guest
        # otherwise each guest have to set explicit a different port
        self.telnet_port = 23
        # this options are using internal only
        self.exclude_options = ['qemu-kvm', 'python-debug', "h", "version"]
        # this settings help to customize the configuration files
        # is_disabled => kvm options is not using
        self.is_disabled = "disabled"
        # is_enabled => kvm option is using and have no value
        self.is_enabled = "enabled"
        # files which should not interpreted as domain config file
        self.exclude_backup_files = [".swp", ]
        # time to wait for sending a enter command to a domain for 
        # grafic environment
        self.shutdown_wait_to_send_enter = None
        # default value to wait till a domain is killed 
        # when the timer is reached
        self.shutdown_time_out = 30 

