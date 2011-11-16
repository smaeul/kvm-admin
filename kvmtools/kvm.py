#!/usr/bin/env python
#
# Module provide the action methodes for a guest.
#

"""
(c) 2007-2011 Jens Kasten <jens@kasten-edv.de> 
"""

import os
import sys
from subprocess import Popen, PIPE
from time import sleep

from kvm_monitor import KvmMonitor


class Kvm(KvmMonitor):
    """
    Class Kvm provide methodes for start, stop and all stuff around this.
    """

    def __init__(self, guest, uuid, pidfile, monitor):
        self._environ_path = "/bin:/usr/bin/:/sbin:/usr/sbin"
        self._pid = None
        self._guest_status = None
        self.guest = guest
        self.uuid = uuid
        self.pidfile = pidfile
        self.socketfile = None
        if "SocketFile" in monitor:
            self.socketfile = monitor['SocketFile']
        # call the parent constructor 
        KvmMonitor.__init__(self, monitor)

    def __del__(self):
        KvmMonitor.__del__(self)
    
    def kvm_monitor(self, command_monitor):
        """Monitor to the qemu-kvm guest on commandline."""
        if self._is_running():
            self.monitor_send(command_monitor)
            data = self.monitor_recieve()
            data = "\n".join([i for i in data])
            print data
        else:
            print "Guest is not running."

    def kvm_boot(self, cmd, bridge):
        """Boot the qemu-kvm guest."""
        if not self._is_running():
            env = {} 
            #env['PATH'] = self._environ_path
            # Fix: add only nessesary path options
            env = os.environ.copy()
            # add the bridge(s) to the enviroment,
            # so the kvm-if[up|down] can use them
            if len(bridge) > 0:
                for key, value in bridge.iteritems():
                    env[key] = value
            try:        
                result = Popen(cmd, env=env, stdin=PIPE, stdout=PIPE)
                result.wait()
            except OSError, e:
                print "Starting guest. [FAIL]"
                return False
            except IOError, e:
                print "Starting guest. [FAIL]"
                return False
            else:
                if self._is_running():
                    print "Starting guest. [OK]" 
                else:
                    print "Starting guest. [FAIL]"
        else:
            print "Guest is already running."

    def kvm_reboot(self):
        """Reboot the guest."""
        if self._is_running():
            if self.monitor_send(self.qemu_monitor["reboot"]):
                print "Rebooting ..."
            else:
                print "Could not send signal reboot to guest."
        else:
            print "Guest is not running."

    def kvm_shutdown(self):
        """Shutdown the guest.
        Its work for windows and linux guests, 
        but not on linux when the Xserver is looked.
        """
        flag = 0
        if self._is_running():
            if self.monitor_send(self.qemu_monitor["shutdown"]):
                self.monitor_send(self.qemu_monitor["enter"])
                print "Shutdown ..."
                while True:
                    # some fancy ticker
                    if flag == 0:
                        sign = "\\"; flag = 1
                    elif flag == 1:    
                        sign = "|"; flag = 2
                    elif flag == 2:
                        sign = "/"; flag = 3
                    elif flag == 3:
                        sign = "-"; flag = 0
                    sys.stdout.write("waiting ... %s\r" % sign)
                    sys.stdout.flush()
                    sleep(0.05)
                    #if self._check_is_running():
                    if not os.path.isfile(self.pidfile):
                        sys.stdout.write("Done.         \n")
                        sys.stdout.flush()
                        sys.exit(0) 
                    else:
                        self._is_running()
            else:
                print "Could not send signal shutdown."
        else:
            print "Guest is not running."

    def kvm_kill(self):
        """Kill the guest.
        Dangerous option, its simply like pull the power cable out.
        """
        if self._is_running():
            try:    
                os.kill(self._pid, 9)
                sleep(0.8)
                if not self._is_running():
                    print "Killed guest. [OK]"
            except OSError, e:
                 print e
        else:
            print "Guest is not running."

    def kvm_status(self):
        """Show information about the guest."""
        if self._is_running():
            process = self._get_process_information()
            print "Name: %s" % process['Name'].split("[")[0]
            print "%s" % process["Status"]
            print "Guest uuid: %s" % process['Uuid']
            print "State: %s" % process['State']
            print "UID: %s" % process['Uid']
            print "GID: %s" % process['Gid']
            print "Groups: %s" % process['Groups']
            print "PID: %s :: PPID: %s" % (process['Pid'], process['PPid'])
            print "VNC: %s" % process["VNC"]
        else:
            print "Guest is not running."

    def _check_is_running(self):
        """Check if the process is running by a given pidfile."""
        if os.path.isfile(self.pidfile):
            with open(self.pidfile) as fd:
                self._pid = int(fd.readline().strip())
                fd.close()
            # check if process alive
            try:
                signal = os.kill(self._pid, 0)
                return True
            except OSError, e:
                return False
            except IOError, e:
                return False
        else:
            p1 = Popen(['ps', 'aux'], stdout=PIPE, stderr=PIPE)
            search = "kvm_" + self.guest
            p2 = Popen(['grep', search], stdin=p1.stdout, stdout=PIPE,
                stderr=PIPE)
            result = p2.communicate()
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

    def _is_running(self):
        """Avoid killing the socket connection, 
        if call boot twice or more on a running guest.
        """
        if self._check_is_running():
            return True
        else:
            if os.path.isfile(self.pidfile):
                os.remove(self.pidfile)
            try:
                os.remove(self.socketfile)
            except OSError, e:
                pass
            return False

    def _get_vnc(self):
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

    def _get_process_information(self):
        """Collect process information from different sources."""
        from subprocess import Popen, PIPE
        process = {}
        process['Uuid'] = self._get_uuid()
        process['Status'] = self._get_status()
        process["VNC"] = self._get_vnc()
        try:
            fd = open(os.path.join("/proc", "%d/status" % self._pid))
            lines = [line.strip().split(':') for line in fd.readlines()]
            fd.close()
            for i in lines:
                process[i[0]] = i[1]
        except OSError, e:
            raise Exception(e)
        except IOError, e:
            raise Exception(e)
        else:
            return process

def main():
    if len(sys.argv) == 3:
        guest = sys.argv[1]
        action = sys.argv[2]
        pid = "/var/run/kvm/%s.pid" % guest
        socket = "/var/run/kvm/%s.socket" % guest
        monitor = {}
        monitor['Type'] = "unix"
        monitor['SocketFile'] = socket
        kvm = Kvm(guest, pid, socket)
        kvm.guest = guest
        if action == "shutdown":
            kvm.kvm_shutdown()
        if action == "status":
            kvm.kvm_status()
        if action == "boot":
            kvm.kvm_boot("no", "no")
        if action == "reboot":
            kvm.kvm_reboot()
        if action == "kill":
            kvm.kvm_kill()
    else:
        print "Usage: %s guest_name action" % (sys.argv[0])

if __name__ == "__main__":
    main()
