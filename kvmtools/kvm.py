#!/usr/bin/env python

"""
Provide the action methodes for a guest.
(c) 2007-2010 Jens Kasten <jens@kasten-edv.de> 
"""

import os
import sys
from subprocess import Popen, PIPE


from kvm_monitor import KvmMonitor


class Kvm(KvmMonitor):
    """
    Class Kvm provide methodes for start, stop and all stuff around this.
    """

    def __init__(self, guest, pidfile, monitor):
        """
        Konstructor.
        """
        self._environ_path = "/bin:/usr/bin/:/sbin:/usr/sbin"
        self._pid = None
        self._guest_status = None
        self.guest = guest
        self.pidfile = pidfile
        self.socketfile = None
        if "SocketFile" in monitor:
            self.socketfile = monitor['SocketFile']
        # call the parent constructor 
        KvmMonitor.__init__(self, monitor)
    
    def __del__(self):
        """
        Destructor.
        """
        KvmMonitor.__del__(self)
    
    def kvm_monitor(self, command_monitor):
        """
        Monitor to the qemu-kvm guest on commandline.
        """
        if self._is_running():
            self.monitor_send(command_monitor)
            data = self.monitor_recieve()
            data = "\n".join([i for i in data])
            print data
        else:
            print "Guest is not running."

    def kvm_boot(self, cmd, bridge):
        """
        Boot the qemu-kvm guest. 
        """
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
            except OSError, e:
                raise Exception(e)
                return False
            except IOError, e:
                raise Exception(e)
                return False
            else:
                print "Starting guest ..." 
        else:
            print "Guest is already running."

    def kvm_reboot(self):
        """
        Reboot the guest.
        """
        if self._is_running():
            if self.monitor_send(self.qemu_monitor["reboot"]):
                print "Rebooting ..."
            else:
                print "Could not send signal reboot to guest."
        else:
            print "Guest is not running."

    def kvm_shutdown(self):
        """
        Shutdown the guest.
        Its work for windows and linux guests, 
        but not on linux when the Xserver is looked.
        """
        flag = 0
        if self._is_running():
            from time import sleep
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
                    if not os.path.isfile(self.pidfile):
                        sys.stdout.write("Done ...     \n")
                        sys.stdout.flush()
                        sys.exit(0) 
            else:
                print "Could not send signal shutdown."
        else:
            print "Guest is not running."

    def kvm_kill(self):
        """
        Kill the guest.
        Dangerous option, its simply like pull the power cable out.
        """
        if self._is_running():
            if os.path.isfile(self.pidfile):
                fd = open(self.pidfile, "r")
                pid = int(fd.readline().strip())
                fd.close
            else:
                pid = self._pid
            try:    
                os.kill(pid, 15)
                os.remove(self.pidfile)
                if self.socketfile:
                    os.remove(self.socketfile)
            except OSError, e:
                 print e
        else:
            print "Guest is not running."
   
    def kvm_status(self):
        """
        Show information about the guest.
        """
        if self._is_running():
            process = self._get_process_information()
            print "Name: %s" % process['Name']
            print "%s" % process["Status"]
            print "Guest uuid: %s" % process['Uuid']
            print "State: %s" % process['State']
            print "UID: %s" % process['Uid']
            print "GID: %s" % process['Gid']
            print "Groups: %s" % process['Groups']
            print "PID: %s :: PPID: %s" % (process['Pid'], process['PPid'])
        else:
            print "Guest is not running."
    
    def _check_is_running_through_pid(self):
        """
        Check if the process is running by a given pid.
        """
        if os.path.isfile(self.pidfile):
            fd = open(self.pidfile)
            self._pid = int(fd.readline().strip())
            fd.close()
            try:
                # check if process alive
                signal = os.kill(self._pid, 0)
            except OSError:
                return False
            else:
                return True
        else:
            return False

    def _get_uuid(self):
        """
        Return the guest uuid.
        """
        self.monitor_send(self.qemu_monitor["uuid"])
        uuid = self.monitor_recieve()[0]
        return uuid

    def _get_status(self):
        """
        Return the status from guest
        """
        self.monitor_send(self.qemu_monitor["status"])
        status = self.monitor_recieve()[0]
        return status

    def _is_running(self):
        """
        Avoid killing the socket connection, if call boot twice or more on a 
        running guest.
        """
        if self._check_is_running_through_pid():
            return True
        else:
            try:
                os.remove(self.pidfile)
                if self.socketfile:
                    os.remove(self.socketfile)
            except:
                # silent throw the error
                return False
            else:
                return False

    def _get_process_information(self):
        """
        Collect process information from different sources.
        """
        from subprocess import Popen, PIPE
        process = {}
        process['Uuid'] = self._get_uuid()
        process['Status'] = self._get_status()
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
