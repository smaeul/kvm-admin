#
# Module BuildConfig collect all data to create a command qemu-kvm command.
# 

"""
(c) 2011 Jens Kasten <jens@kasten-edv.de>
"""

import os
import random
import string
import re

from kvmtools.config.parser import Parser


class BuildConfig(Parser):
    
    def __init__(self):
        self.config = {}
        self.monitor_options = {}
        self.bridge = {}

    def build_config(self):
        """Load domain and global config and then merge them."""
        kvm_conf_file = self.parse_config(self.kvm_conf_file)
        kvm_domain_file = self.parse_config(self.kvm_domain_file)
        self.config = self.merge_configs(kvm_conf_file, kvm_domain_file)
        if not self.config:
            return None
        self._add_name()
        self._add_uuid()
        self._add_pidfile()
        self._add_monitor()
        self._add_net()

    def _add_pidfile(self):
        """Append the pidfile option to the config dictionary or reverse."""
        if "pidfile" not in self.config:
            pidfile = os.path.join(self.kvm_run_path, self.kvm_pidfile)
            self.config["pidfile"] = pidfile
        else:
            self.kvm_pidfile = self.config["pidfile"]

    def _add_uuid(self):
        """Append an unique uuid to the config dictionary."""
        if "uuid" in self.config:
            check_uid = re.match(r"([a-z,A-z,0-9]{8})-([a-z,A-Z,0-9]{4})-([a-z,A-Z,0-9]{4})-([a-z,A-Z,0-9]{4})-([a-z,A-Z,0-9]{12})", self.config["uuid"])
            if not check_uid:
                msg = "Your uuid has wrong format, you can delete it, the script does generate a correct new one."
                self.kvm_error(msg)
                self.kvm_error(self.config["uuid"])
            return
        random.seed(os.urandom(8))
        charset = string.digits + "abcdef"
        eight = "".join(random.sample(charset, 8))
        four_first = "".join(random.sample(charset, 4))
        four_second = "".join(random.sample(charset, 4))
        four_third = "".join(random.sample(charset, 4))
        twelve =  "".join(random.sample(charset, 12))
        uuid = "-".join([eight, four_first, four_second, four_third, twelve])
        # inster the uuid into domain config file if it not exists
        with open(self.kvm_domain_file, "a+") as fd:
            fd.write("uuid = %s\t# autogenerted and instert from script\n" % uuid)
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

    def _add_net(self):
        """Examine the -net tap option for ifname and additional scripts and 
        bridge strings, if not -tap option don't touch the values.
        """
        temp = {} 
        counter = 0
        if "net" not in self.config:
            return False
        for key, value in self.config["net"].iteritems():
            if value.startswith("tap"):
                # search for ifname otherwise set it from domain_name name
                if re.search("ifname", value):
                    ifname = re.search("ifname=([a-zA-Z0-9]+)", value)
                    bridge_if = ifname.group(1)
                else:
                    ifname = "=".join(["ifname", 
                        self.kvm_domain_name + str(counter)])
                    bridge_if = self.kvm_domain_name + str(counter)
                    if re.match("tap,", value):
                        value = re.sub("tap,", "tap,%s,", value) % ifname
                    else:
                        value = re.sub("tap", "tap,%s", value) % ifname
                    counter += 1
                assert type(bridge_if) is str, "ifname is not a string %s" % ifname
                # build the bridge key for exporting to the environ   
                bridge_key = "_".join(["kvm_bridge", bridge_if])
                assert type(bridge_key) is str, "bridge_key is not a str: %s" % \
                    bridge_key
                # search for bridge value
                if re.search("bridge", value):
                    bridge = re.search("(,|)bridge=([a-zA-Z0-9]+)", value)
                    # remove the bridge from string
                    value = value.replace(bridge.group(0), "")
                    # assign bridge for exporting the bridge name
                    self.bridge[bridge_key] = bridge.group(2)
                else:
                    msg = "Missing second Value for bridge.\n"
                    msg += "Syntax example: bridge=br0"
                    raise Exception(msg)
                # search for script 
                if not re.search("script", value):
                    ifup = "=".join(["script",
                        os.path.join(self.kvm_script_dir, 'kvm-ifup')])
                    value = ",".join([value, ifup])
                # search for downscript
                if not re.search("downscript", value):
                    ifdown = "=".join(["downscript",
                        os.path.join(self.kvm_script_dir, 'kvm-ifdown')])
                    value = ",".join([value, ifdown])
                # add the cleaned value to temporary dictionary
                temp[key] = value
            else:                    
                temp[key] = value
        # add the cleand temp dictionary back to config        
        self.config["net"] = temp
