#
# Modulde which contain the methodes which can call from commandline
#

"""
(c) 2011-2012 Jens Kasten <jens@kasten-edv.de>
"""

import os
import sys
from subprocess import Popen, PIPE
from time import sleep, time

from kvmtools.kvm.domain import Domain


class Action(Domain):

    def __init__(self):
        Domain.__init__(self)
        self.kvm_status_full = False

    def kvm_error(self, error_message):
        """Append a error message to error list."""
        self.kvm_errors.append(error_message)

    def available_actions(self):
        """Return all methods which start with kvm_ and end with _action."""
        actions = []
        for action in dir(self):
            if action.startswith("kvm_") and action.endswith("_action"):
                methode = action.replace("kvm_", "").replace("_action", "")
                actions.append(methode)
        return actions

    def kvm_show_action(self):
        """Show the qemu-kvm command as string."""
        print self.command[1]

    def kvm_modify_action(self):
        """Modify a qemu-kvm domain configuration file."""
        self.modify()

    def kvm_create_action(self):
        """Create a basic qemu-kvm domain configuration file."""
        if os.path.isfile(self.kvm_domain_file):
            self.modify()
        else:
            self.create()

    #def kvm_migrate_action(self, command_monitor):
    #    self.kvm_monitor_action(command_monitor)

    def kvm_monitor_action(self, command_monitor):
        """Monitor a qemu-kvm domain."""
        if not self.is_running():
            print ("Guest is not running.")
            return
        self.monitor_send(command_monitor)
        data = self.monitor_recieve()
        data = "\n".join([i for i in data])
        print data

    def kvm_boot_action(self):
        """Boot a qemu-kvm domain."""
        if self.is_running():
            print ("Guest already running.")
            return True
        env = os.environ.copy()
        # add the  to the enviroment
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
        """Reboot a qemu-kvm domain."""
        if not self.is_running():
            print ("Guest is not running.")
            return False
        if not self.monitor_send(self.qemu_monitor["reboot"]):
            print ("Could not send signal reboot to guest.")

    def kvm_shutdown_action(self):
        """Shutdown a qemu-kvm domain.
        Its work for windows and linux guests, 
        but not on linux when the Xserver is looked.
        """
        if not self.is_running():
            print ("Guest is not running.")
            return
        flag = 0
        if self.monitor_send(self.qemu_monitor["shutdown"]):
            # set a time  out to wait, that the shutdown dialog appears
            if self.shutdown_wait_to_send_enter:
                sleep(self.shutdown_wait_to_send_enter)
                self.monitor_send(self.qemu_monitor["enter"])
            # set start timer
            timer = time() 
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
                if not self.is_running():
                    sys.stdout.write("Done.         \n")
                    sys.stdout.flush()
                    sys.exit(0) 
                else:
                    sys.stdout.write("waiting ... %s\r" % sign)
                    sys.stdout.flush()
                    sleep(0.05)
                # when the time out is reached kill the qemu-kvm domain
                # this is only usefull for init.d system 
                # otherwise if the domain could from any reason not shutdown
                # the whole shutdown process is blocked
                if (timer + self.shudown_time_out) < time():
                    self.kvm_kill_action()
        else:
            print ("Could not send signal shutdown.")

    def kvm_kill_action(self):
        """Kill a qemu-kvm domain.
        Dangerous option, its simply like pull the power cable out.
        """
        if not self.is_running():
            print ("Guest is not running.")
            return False
        try:    
            os.kill(self.kvm_pid, 9)
            sleep(0.8)
            self.is_running()
            sys.exit(0)
        except OSError, error_msg:
            print error_msg
            self.is_running()
            sys.exit(1)

    def _status_all(self):
        """Show status information form all running qemu-kvm domains."""
        domains = {}
        # list all files in run dir and get pidfile socketfile and domain name
        for i in os.listdir(self.kvm_run_dir):
            domain_name = i.rsplit(".", 1)[0]
            if not domain_name in domains:
                domains[domain_name] = {}
            if i.endswith(".pid"):
                domains[domain_name]["pidfile"] = os.path.join(self.kvm_run_dir, i)
            if i.endswith(".socket"):
                domains[domain_name]["socketfile"] = os.path.join(self.kvm_run_dir, i)
        # iter over the domains and set the necessary values on the fly
        counter = len(domains)
        for domain in domains.iterkeys():
            self.kvm_pidfile = domains[domain]["pidfile"]
            self.kvm_socketfile = domains[domain]["socketfile"]
            self.kvm_domain_name = domain
            self.monitor_open()
            self._get_uuid()
            self._get_status()
            self._get_process_info()
            print ("Domain name: %s :: Process name: %s" % \
                (domain, self.kvm_process_name))
            print ("Domain uuid: %s" % self.kvm_process_uuid)
            print ("%s :: Process state: %s" % \
                (self.kvm_process_status, self.kvm_process_state))
            if self.kvm_status_full:
                self._get_vnc()
                print "UID: %s" % self.kvm_process_uid
                print "GID: %s" % self.kvm_process_gid
                print "Groups: %s" % self.kvm_process_groups
                print "PID: %s :: PPID: %s" % \
                    (self.kvm_process_pid, self.kvm_process_ppid)
                print ("VNC information")
                print self.kvm_process_vnc
            self.monitor_close()
            # show only line for seperation if more than one domains
            if counter > 1:
                print "-" * 80
            counter -= 1

    def kvm_status_action(self):
        """Show information about qemu-kvm domain(s)."""
        if self.kvm_domain_name == "all":
            self._status_all()
            return True
        if not self.is_running():
            print ("Guest is not running.")
            return False
        self.get_process_information()
        print ("Domain name: %s :: Process name: %s" % \
            (self.kvm_domain_name, self.kvm_process_name))
        print ("Domain uuid: %s" % self.kvm_process_uuid)
        print ("%s :: Process state: %s" % \
            (self.kvm_process_status, self.kvm_process_state))
        print "UID: %s" % self.kvm_process_uid
        print "GID: %s" % self.kvm_process_gid
        print "Groups: %s" % self.kvm_process_groups
        print "PID: %s :: PPID: %s" % \
            (self.kvm_process_pid, self.kvm_process_ppid)
        print ("VNC information")
        print self.kvm_process_vnc
