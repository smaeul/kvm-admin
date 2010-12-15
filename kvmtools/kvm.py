#!/usr/bin/env python

"""
Provide the action method for a guest.
(c) 2007-2010 Jens Kasten <jens@kasten-edv.de> 
"""

import os
import sys
import socket
import time
from subprocess import Popen, PIPE 


class Kvm(object):
    """
    Class Kvm
    """

    def __init__(self, pidfile, socketfile):
        self.pidfile = pidfile
        self.socketfile = socketfile

    def open(self):        
        """
        Open a socket to connect to the qemu-kvm monitor.
        """
        if os.path.exists(self.socketfile):
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                self.socket.connect(self.socketfile)
            except socket.error, e:
                print str(e)


    def close(self):
        """
        Close the opened socket. 
        """    
        try:
            self.socket.close()
        except AttributeError:
           pass 


    def build_command(self, config):
        """
        Return a tuple with a list to execute via subprocess
        and a string to display it.
        """
        from qemu_kvm_options import qemu_kvm_options

        cmd_execute = []
        cmd_string = ""

        # Start to build a list, first add the qemu-kvm binary
        cmd_execute.append(config["qemu-kvm"])
        # iterate over the user config
        for key, value in config.iteritems():
            # check if key is in qemu_kvm_options
            if key in qemu_kvm_options:
                if isinstance(value, dict):
                    for i in value.itervalues():
                        cmd_execute.append(''.join(['-', key]))
                        cmd_execute.append(i)
                elif "enabled" != value:
                    # this qemu-kvm option have an option, so add -key value
                    cmd_execute.append(''.join(['-', key]))
                    cmd_execute.append(value)
                else:
                    # this qemu-kvm option don't have an option, 
                    # so only add -key
                    cmd_execute.append(''.join(['-', key]))
        # build a string for to display on terminal output
        cmd_string = " ".join([value for value in cmd_execute])
        return (cmd_execute, cmd_string)


    def _kvm_boot(self, cmd, bridge):
        """
        Boot the qemu-kvm guest. 
        """
        env = {} 
        env = os.environ.copy()
        if len(bridge) > 0:
            for key, value in bridge.iteritems():
                env[key] = value
        print "Booting '%s'" % sys.argv[1]                
        result = Popen(cmd, env=env, stdin=PIPE, stdout=PIPE)
        try:
            output = result.communicate()[0]
            if len(output) > 0:
                print output
        except OSError, e:
            print str(e)


    def _kvm_shutdown(self):
        """
        Shutdown the guest.
        Its work for windows and linux guests, 
        but not on linux when the Xserver is looked.
        """
        try:
            if not os.path.isfile(self.pidfile):
                msg = "Could not found pidfile."
                raise Exception(msg)
            print "Shutdown '%s' ..." % sys.argv[1]
            self.socket.send('system_powerdown\n')
            time.sleep(0.5)
            #for guest which need a enter to shutdown
            self.socket.send('sendkey ret\n')
            flag = 0
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
                time.sleep(0.05)
                if not os.path.isfile(self.pidfile):
                    sys.stdout.write("Done ...     \n")
                    sys.exit(0) 
        except AttributeError, e:
            print str(e)
            print "Guest already down."


    def _kvm_reboot(self):
        """
        Reboot the guest.
        """
        try:
            print "Rebooting '%s' ..." % self.kvm
            self.socket.send('sendkey ctrl-alt-delete 200\n')
        except AttributeError:
            print "Guest is down, can't reboot."

    def _get_uuid(self):
        """
        Return the guest uuid.
        """
        try:
            self.socket.send("info uuid\n")
            time.sleep(0.2)
            data = self.socket.recv(1024)
            status = data.split('\r\n')
            if len(status) > 2:
                return status[2]
            else:
                return False
        except AttributeError, e:
            print str(e)
            
    def _process_information(self):
        """
        Collect process information from different sources.
        """
        try:
            process = {}
            # get the unique uuid from guest monitor
            # use uuid is available ottherwise use processname
            uuid = self._get_uuid()
            if uuid:
                process['uuid'] = "Guest uuid: %s" % uuid
            else:                 
                name = "Guest name: %s" % self.guest
                uuid = "process=%s" % self.guest
                process['uuid'] = name     
            # find data from process using ps and grep
            ps = Popen(["ps", "aux"], stdout=PIPE)
            grep = Popen(["grep", uuid], stdin=ps.stdout, stdout=PIPE)
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
            return process
        except AttributeError, e:
            print "error: %s" % str(e)
        except Exception, e:
            print str(e)
    
    def _kvm_status(self):
        """
        Show the status if running or paused the guest.
        """
        try:
            process = self._process_information()
            self.socket.send("info status\n")
            # need some time to get all output from the monitor
            time.sleep(0.222)
            data = self.socket.recv(1024)
            status = data.split("\r\n")
            if len(status) > 2:
                print "%s" % (status[1])
                print process['uuid']
                print "State: %s" % process['state']
                print "User: %s ::  Groups: %s" % (process['user'], process['groups'])
                print "UID: %s :: GID: %s" % (process['uid'], process['gid'])
                print "PID: %s :: PPID: %s" % (process['pid'], process['ppid'])
                print "Cpu usage: %s%%" % process['cpu']
                print "Memory usage: %s%%" % process['mem']
                print "Start: %s" % process['start']
                print "Time: %s" % process['time']
            else:
                print "Monitor is busy, wait a moment and try again."
        except AttributeError, e:
            print str(e)
        except socket.error, e:
            print  str(e)

    def _kvm_kill(self):
        """
        Kill the guest.
        Dangerous option, its simply like pull the power cable out.
        """
        if os.path.isfile(self.pidfile):
            try:
                fd = open(self.pidfile, "r")
                pid = int(fd.readline().strip())
                os.kill(pid, 15)
                os.remove(self.pidfile)
                os.remove(self.socketfile)
            except OSError:
                # Fixme find domain name in process
                pass
        else:
            print "Could not found pidfile."
            print "Guess guest is not running and was proper shutdown."


    def _kvm_monitor(self, cmd_monitor):
        """
        Monitor to the qemu-kvm guest on commandline.
        """
        try:
            self.socket.send(cmd_monitor + "\n")
            time.sleep(0.2)
            data = self.socket.recv(4096)
            status = data.split('\r\n')
            i = 2
            if len(status) > 2:
                while i < len(status)-1 :
                    print "%s" % (status[i])
                    i += 1
            else:
                print "Get nothing from monitor."
        except AttributeError:
            print "Guest is down."


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
        kvm.open()
        if action == "shutdown":
            kvm._kvm_shutdown()
        if action == "status":
            kvm._kvm_status()
        # close socket to monitor
        kvm.close()
    else:
        print "Usage: %s guest_name action" % (sys.argv[0])

if __name__ == "__main__":
    main()
