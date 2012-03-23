#
# header file
# try to collect all attribute which can be changed
#

"""
(c) 2011 Jens Kasten <jens@kasten-edv.de>
"""

class Header(object):
    """Contain all attribute to store filename or paths and some other stuff.
    """
    
    def __init__(self):
        # base direcotry configs, and scripts 
        self.kvm_base_config_dir = "/etc/kvm"
        # subdirecotories from self.base_dir
        # directory name to store the ifdown and ifup scripts
        self._kvm_script_dir = 'scripts'
        # directory name to store the guest configuration files
        self._kvm_domain_dir = 'domains'
        # directory name to store the global configuration file
        self._kvm_conf_dir = 'config'
        # name for global configuration file
        self._kvm_conf_name = 'kvm.cfg'
        # default telnet port 23, can only use once at time in one guest
        # otherwise each guest have to set expliciet a different port
        self.telnet_port = 23
        # default directory for pidfile,and socketfile
        self.kvm_run_path = '/var/run/kvm'
        # this exclude_options are using internal only
        self.exclude_options = ['qemu-kvm', 'python-debug', "h", "version"]
        # file name for qemu kvm options
        self.qemu_kvm_options_file_name = "qemu_kvm_options.py"
        # search path's
        self.search_paths = ["/bin", "/sbin", 
                             "/usr/bin", "/usr/sbin", 
                             "/usr/local/sbin", "/usr/local/bin"]
        # setting for qemu-kvm 
        self.is_disabled = "disabled"
        # setting for qemu-kvm options
        self.is_enabled = "enabled"
        self.qemu_kvm_error_message = []


