#
# Modulde which contain the methodes which can call from commandline
#

"""
(c) 2011 Jens Kasten <jens@kasten-edv.de>
"""

import os
import sys
from subprocess import Popen, PIPE
from time import sleep

from kvmtools.kvm.monitor import KvmMonitor
from kvmtools.config.domain import Domain
from kvmtools.kvm.build_config import BuildConfig
from kvmtools.kvm.build_command import BuildCommand
from kvmtools.system_utils import System

class KvmAction(Domain, BuildConfig, BuildCommand, KvmMonitor, System):
    
    def __init__(self):
        Domain.__init__(self)
        BuildConfig.__init__(self)
        BuildCommand.__init__(self)
        System.__init__(self)
        self.command = ()
        self.socket = None

    def load_command(self):
        """Load config"""
        try:
            self.build_config()
        except Exception:
            self.kvm_modify_action()
        self.command = self.build_command()
        KvmMonitor.__init__(self)

    def available_actions(self):
        """Return all methods which start with kvm_ and end with _action."""
        actions = []
        for action in dir(self):
            if action.startswith("kvm_") and action.endswith("_action"):
                methode = action.replace("kvm_", "").replace("_action", "")
                actions.append(methode)
        return actions
   
    def kvm_show_action(self):
        """show the command as string"""
        print self.command[1]

    def kvm_modify_action(self):
        """Modify a domain configuration file."""
        self.modify()

    def kvm_create_action(self):
        """Create a domain configuration file."""
        if os.path.isfile(self.kvm_domain_file):
            self.modify()
        else:
            self.create()

    def kvm_migrate_action(self, command_monitor):
        self.kvm_monitor_action(command_monitor)

    def kvm_monitor_action(self, command_monitor):
        """Monitor to the qemu-kvm guest on commandline."""
        if not self.is_running(self.kvm_pid):
            print ("Guest is not running.")
            return
        self.monitor_send(command_monitor)
        data = self.monitor_recieve()
        data = "\n".join([i for i in data])
        print data

    def kvm_boot_action(self):
        """Boot the qemu-kvm guest."""
        if self.is_running(self.kvm_pid):
            print ("Guest already running.")
            return True
        env = os.environ.copy()
        # add the bridge(s) to the enviroment
        if len(self.bridge) > 0:
            for key, value in self.bridge.iteritems():
                env[key] = value
        try:
            result = Popen(self.command[0], env=env, stdin=PIPE, stdout=PIPE)
            result.wait()
            return (True, "")
        except OSError, error_msg:
            return (False, error_msg)
        except IOError, error_msg:
            return (False, error_msg)

    def kvm_reboot_action(self):
        """Reboot the guest."""
        if not self.is_running(self.kvm_pid):
            print ("Guest is not running.")
            return False
        if self.monitor_send(self.qemu_monitor["reboot"]):
            print ("Rebooting ...")
        else:
            print ("Could not send signal reboot to guest.")

    def kvm_shutdown_action(self):
        """Shutdown the guest.
        Its work for windows and linux guests, 
        but not on linux when the Xserver is looked.
        """
        if not self.system.is_running(self.kvm_pid):
            print ("Guest is not running.")
        flag = 0
        if self.monitor_send(self.qemu_monitor["shutdown"]):
            self.monitor_send(self.qemu_monitor["enter"])
            print ("Shutdown ...")
            while True:
                # some fancy ticker
                if flag == 0:
                    sign = "\\" 
                    flag = 1
                elif flag == 1:    
                    sign = "|"
                    flag = 2
                elif flag == 2:
                    sign = "/"
                    flag = 3
                elif flag == 3:
                    sign = "-"
                    flag = 0
                sys.stdout.write("waiting ... %s\r" % sign)
                sys.stdout.flush()
                sleep(0.05)
                # if self._check_is_running():
                if not os.path.isfile(self.kvm_pidfile):
                    sys.stdout.write("Done.         \n")
                    sys.stdout.flush()
                    sys.exit(0) 
                if not self.is_running(self.kvm_pid):
                    if os.path.isfile(self.kvm_pidfile):
                        os.remove(self.kvm_pidfile)
            else:
                print ("Could not send signal shutdown.")

    def kvm_kill_action(self):
        """Kill the guest.
        Dangerous option, its simply like pull the power cable out.
        """
        if not self.is_running(self.kvm_pid):
            print ("Guest is not running.")
            return False
        try:    
            os.kill(self.kvm_pid, 9)
            sleep(0.8)
            sys.exit(0)
        except OSError, error_msg:
            print error_msg
            sys.exit(1)

    def kvm_status_action(self):
        """Show information about the guest."""
        if not self.is_running(self.kvm_pid):
            print ("Guest is not running.")
            return False
        process = self.get_process_information()
        info = self.get_process_info(self.kvm_pid)
        print "Name: %s" % process['Name'].split("[")[0]
        print "Cmdline: %s" % info["cmdline"]
        print "rss in %d KB" % info["rss"]
        print "vms in %d KB" % info["vms"]
        print "%s" % process["Status"]
        print "Guest uuid: %s" % process['Uuid']
        print "State: %s" % process['State']
        print "UID: %s" % process['Uid']
        print "GID: %s" % process['Gid']
        print "Groups: %s" % process['Groups']
        print "PID: %s :: PPID: %s" % (process['Pid'], process['PPid'])
        print "VNC: %s" % process["VNC"]

    def _check_is_running(self):
        """Check if the process is running by a given pidfile."""
        if os.path.isfile(self.pidfile):
            with open(self.pidfile) as file_descriptor:
                self._pid = int(file_descriptor.readline().strip())
                file_descriptor.close()
            # check if process alive
            try:
                os.kill(self._pid, 0)
                return True
            except OSError:
                return False
            except IOError:
                return False
        else:
            process1 = Popen(['ps', 'aux'], stdout=PIPE, stderr=PIPE)
            search = "kvm_" + self.guest
            process2 = Popen(['grep', search], stdin=process1.stdout, 
                stdout=PIPE, stderr=PIPE)
            result = process2.communicate()
            status = result[0].split("\n")
            # search for pid
            if len(status) > 1:
                # iterate over the ps aux output per line
                for i in status:
                    if not "grep" in i:
                        pid = i.split(" ")
                        # remove first element, its the user name
                        del pid[0]
                        for j in pid:
                            if j == "":
                                continue
                            else:
                                # found pid 
                                self._pid = int(j)
                                return True
                return False
            else:
                return False
