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
            self.socket.send('system_powerdown\n')
            time.sleep(1)
            # for guest which need a enter to shutdown
            self.socket.send('sendkey ret\n')
        except AttributeError:
            print "Guest already down."


    def _kvm_reboot(self):
        """
        Reboot the guest.
        """
        try: 
            self.socket.send('sendkey ctrl-alt-delete 200\n')
        except AttributeError:
            print "Guest is down, can't reboot."


    def _kvm_status(self):
        """
        Show the status if running or paused the guest.
        """
        try: 
            self.socket.send("info status\n")
            # need some time to get all output from the monitor
            time.sleep(0.222)
            data = self.socket.recv(1024)
            status = data.split('\r\n')
            if len(status) > 2:
                print "%s" % (status[2])
            else:
                print "Monitor is busy, wait a moment and try again."
        except AttributeError:
            print "Guest ist down"
        except socket.error, e:
            str(e)

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

        
