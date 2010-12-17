#!/usr/bin/env python

"""
Provide the action method for a guest.
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

    def __init__(self, guest, pidfile, socketfile):
        """
        Konstructor.
        """
        self._pid = None
        self._guest_status = None
        self.guest = guest
        self.pidfile = pidfile
        self.socketfile = socketfile
        # call the parent constructor
        KvmMonitor.__init__(self)
    
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

    def kvm_boot(self, cmd, bridge):
        """
        Boot the qemu-kvm guest. 
        """
        if self._is_running():
            print "Not booting. Already running ..."
            return
        env = {} 
        env = os.environ.copy()
        # add the bridge(s) to the enviroment, so the kvm-if[up|down] can use them
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
            print "Booting ..."

    def kvm_reboot(self):
        """
        Reboot the guest.
        """
        if self._is_running():
            if self.monitor_send(self.qemu_monitor["reboot"]):
                print "Rebooting ..."
            else:
                print "Could not send signal reboot to guest. break ..."
        else:
            print "Could not reboot. Guest not running ..."

    def kvm_shutdown(self):
        """
        Shutdown the guest.
        Its work for windows and linux guests, 
        but not on linux when the Xserver is looked.
        """
        flag = 0
        if not self._is_running():
            print "Could not shutdown guest. Not running ..."
        else:
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
                        sys.exit(0) 
            else:
                print "Could not send signal shutdown. break ..."

    def kvm_kill(self):
        """
        Kill the guest.
        Dangerous option, its simply like pull the power cable out.
        """
        if not self._is_running():
            print "Could not kill guest. Not running ..."
        else:
            if os.path.isfile(self.pidfile):
                fd = open(self.pidfile, "r")
                pid = int(fd.readline().strip())
                fd.close
            else:
                pid = self._pid
            try:    
                os.kill(pid, 15)
                os.remove(self.pidfile)
                os.remove(self.socketfile)
            except OSError, e:
                 print e
   
    def kvm_status(self):
        """
        Show information about the guest.
        """
        if self._is_running():
            process = self._get_process_information()
            print self._guest_status
            print "Guest uuid: %s" % process['uuid']
            print "State: %s" % process['state']
            print "User: %s ::  Groups: %s" % (process['user'], process['groups'])
            print "UID: %s :: GID: %s" % (process['uid'], process['gid'])
            print "PID: %s :: PPID: %s" % (process['pid'], process['ppid'])
            print "Cpu usage: %s%%" % process['cpu']
            print "Memory usage: %s%%" % process['mem']
            print "Start: %s" % process['start']
            print "Time: %s" % process['time']
        else:
            print "No guest information through monitor available."
    
    # from here the internal methodes begin
    def _check_is_running_through_monitor(self):
        """
        Check if the guest running or paused and return True or False.
        Use qemu monitor status.
        """
        if self.monitor_send(self.qemu_monitor["status"]):
            data = self.monitor_recieve()[0]
            # clear monitor
            self.monitor_send("")
            if "running" in data:
                self._guest_status = data
                return True
            elif "paused" in data:
                self._quest_status = data
                return True
        else:
            return False

    def _check_is_running_through_system(self):
        """
        Check if the process is running throug system information.
        """
        ps = Popen(["ps", "aux"], stdout=PIPE)
        result = Popen(["grep", "process=%s" % self.guest], stdin=ps.stdout, stdout=PIPE)
        result = result.communicate()[0].split("\n")
        if len(result) > 2:
            self._pid =  "".join([result[0].split(" ")[6], "\n"])
            print "Create new pidfile because no pidfile exists, but process is running."
            fd = open(self.pidfile, "w")
            fd.write(self._pid)
            fd.close()
            return True
        else:
            return False
      
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
            except OSError, e:
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

    def _is_running(self):
        """
        Avoid killing the socket connection, if call boot twice or more on a 
        running guest.
        """
        if self._check_is_running_through_monitor() or\
            self._check_is_running_through_pid() or\
            self._check_is_running_through_system():
            return True 
        else:
            try:
                os.remove(self.pidfile)
                os.remove(self.socketfile)
            except OSError, e:
                # silent throw the error
                pass
            return False


    def _get_process_information(self):
        """
        Collect process information from different sources.
        """
        from subprocess import Popen, PIPE
        process = {}
        process['uuid'] = self._get_uuid()
        try:
            # find data from process using ps and grep
            ps = Popen(["ps", "aux"], stdout=PIPE)
            grep = Popen(["grep", process['uuid']], stdin=ps.stdout, stdout=PIPE)
            input, output = grep.communicate()
            process_data = input.split("\n")[0].split(" ")
            # clean process_data, remove empty value
            process_data  = [i for i in process_data if len(i) > 0]
            # assign values to dict process
            process['user'] = process_data[0]
            process['pid'] = process_data[1]
            process['cpu'] = process_data[2]
            process['mem'] = process_data[3]
            process['start'] = process_data[8]
            process['time'] = process_data[9]
            # get more info about process from proc
            fd = open(os.path.join("/proc", "%s/status" % process['pid']))
            lines = [line.strip().split(':') for line in fd.readlines()]
            fd.close()
            # assign value to dict process
            process['name'] = lines[0][1]
            process['state'] = lines[1][1]
            process['ppid'] = lines[4][1].replace('\t', '')
            process['uid'] = lines[6][1].split('\t')[1]
            process['gid'] = lines[7][1].split('\t')[1]
            process['fdsize'] = lines[8][1]
            process['groups'] = lines[9][1]
        except OSError, e:
            raise Exception(e)
        except IOError, e:
            raise Exception(e)
        else:
            return process

    def _emerge_socket(self, command):
        """
        Use if the socket was removed.
        """
        command = "info status"
        from time import sleep
        import socket
        self._is_running()
        print self._pid
        if self._pid:
            # search for socket in /proc/pid/fd
            socketfile = "/proc/" + str(self._pid) + "/fd/3"
            print socketfile
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(socketfile)
            sock.send(command + "\n")
            sleep(0.2)
            data = sock.recv(4096)
            data = data.split("\r\n")
            print data
            


def main():
    if len(sys.argv) == 3:
        guest = sys.argv[1]
        action = sys.argv[2]
        pid = "/var/run/kvm/%s.pid" % guest
        socket = "/var/run/kvm/%s.socket" % guest
        print "Instancied Kvm()"
        kvm = Kvm(pid, socket)
        kvm.guest = guest
        # open socket to monitor
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
        if action == "emerge":
            kvm._emerge_socket("info status")
    else:
        print "Usage: %s guest_name action" % (sys.argv[0])

if __name__ == "__main__":
    main()
