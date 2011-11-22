#
# validate config
#

"""
(c) 2011 Jens Kasten <jens@kasten-edv.de>
"""

import os
import sys
import re
try:
    from kvmtools.qemu_kvm_options import qemu_kvm_options
except ImportError, error_msg:
    print error_msg
    sys.exit(1)


class ValidateConfig(object):
    """Validate the domain config file against qemu-kvm options."""

    def __init__(self):
        self.bridge = {}

    def check_config(self, config):
        """check the config files if the have valid qemu-kvm options."""
        for key in config.iterkeys():
            # ignore the exclude options form check
            if key in self.exclude_options:
                continue
            if key not in qemu_kvm_options:
                return False
        else:
            return True

    def _qemu_kvm_script(self, script_option):
        """Return the absoulute path for ifup or ifdown script."""
        script_option = "".join(["kvm-", script_option])
        script = os.path.join(self.kvm_script_dir, script_option)
        return script

    def _check_net_tap(self):
        """Examine the -net tap option for ifname and additional scripts and 
        bridge strings.
        """
        temp = {} 
        counter = 0
        for key, value in self.config["net"].iteritems():
            if value.startswith("tap"):
                # search for ifname otherwise set it from guest name
                if re.search("ifname", value):
                    temp_ifname = re.search(",ifname=([a-zA-Z0-9]+)", value)
                    ifname = temp_ifname.group(1)
                else:
                    ifname = "".join([self.kvm_domain_name, str(counter)])
                    temp_ifname = "=".join(["ifname", ifname])
                    if re.match("tap,", value):
                        value = re.sub("tap,", "tap,%s,", value) % temp_ifname
                    else:
                        value = re.sub("tap", "tap,%s", value) % temp_ifname
                    counter += 1
                # build the bridge key    
                bridge_key = "_".join(["bridge", ifname])
                # search for bridge otherwise raise an exception,
                # because this value is needed
                if re.search("bridge", value):
                    temp_bridge = re.search(",bridge=([a-zA-Z0-9]+)", value)
                    # get the bridge name from searched group
                    bridge = temp_bridge.group(1)
                    # remove the bridge from string
                    value = value.replace(temp_bridge.group(0), "")
                else:
                    msg = "Missing second Value for bridge.\n"
                    msg = "".join([msg, "Syntax example: bridge=br0"])
                    raise Exception(msg)
                # assign bridge for exporting the bridge name
                self.bridge[bridge_key] = bridge
                # search for script 
                if not re.search("script", value):
                    ifup = "=".join(["script", self._qemu_kvm_script('ifup')])
                    value = ",".join([value, ifup])
                # search for downscript
                if not re.search("downscript", value):
                    ifdown = "=".join(["downscript", 
                                        self._qemu_kvm_script('ifdown')])
                    value = ",".join([value, ifdown])
                # add the cleaned value to temporary dictionary
                temp[key] = value
            else:                    
                temp[key] = value
        # add the cleand temp dictionary back to config        
        self.config["net"] = temp
        return True
    
    def _get_pid(self):
        """Set pif if pidfile is available"""
        if os.path.isfile(self.kvm_pidfile):
            with open(self.kvm_pidfile) as fd:
                self.kvm_pid = int(fd.readline().strip())

   
    def _get_vnc(self):
        """Return vnc info."""
        self.monitor_send("info vnc")
        vnc = self.monitor_recieve()
        vnc = "\n".join(vnc)
        return vnc

    def _get_uuid(self):
        """Return the guest uuid."""
        self.monitor_send(self.qemu_monitor["uuid"])
        uuid = self.monitor_recieve()[0]
        return uuid

    def _get_status(self):
        """Return the status from guest."""
        self.monitor_send(self.qemu_monitor["status"])
        status = self.monitor_recieve()[0]
        return status

    def get_process_information(self):
        """Collect process information from different sources."""
        process = {}
        process['Uuid'] = self._get_uuid()
        process['Status'] = self._get_status()
        process["VNC"] = self._get_vnc()
        try:
            _fd = open(os.path.join("/proc", "%d/status" % self.kvm_pid))
            lines = [line.strip().split(':') for line in _fd.readlines()]
            _fd.close()
            for i in lines:
                process[i[0]] = i[1]
        except OSError, error_msg:
            raise Exception(error_msg)
        except IOError, error_msg:
            raise Exception(error_msg)
        else:
            return process 
