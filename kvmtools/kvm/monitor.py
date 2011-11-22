#!/usr/bin/env python
#
# Module to handle the monitor stuff.
#

"""
(c) 2009-2011 Jens Kasten <jens@kasten-edv.de>
"""

import socket
import time


class KvmMonitor(object):
    """
    Class for connect and disconnect to a qemu monitor socket.
    Additional send data to and recieve data from monitor.
    """

    def __init__(self):
        # keep the socket
        self.socket = None
        # flag if socket can acces
        self.socket_status = False
        # data for method socket_recieve
        self.recieve_data = {
            "data_offset_first_call": 2, 
            "data_offset_second_call": 1,
        } 
        # predefined qemu monitor options
        self.qemu_monitor = {
            "shutdown": "system_powerdown",
            "reboot": "sendkey ctrl-alt-delete 200",
            "enter": "sendkey ret",
            "status": "info status",
            "uuid": "info uuid",
            "network": "info network",
        }
        self._monitor_open()

    def __del__(self):
        """Close to socket when exit the program."""
        self._monitor_close()

    #########################################
    # monitor via unix socket or tcp socket #
    #########################################
    def _monitor_open(self):        
        """Open a socket to connect to the qemu-kvm monitor."""
        if self.monitor_options['Type'] == 'unix': 
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                self.socket.connect(self.kvm_socketfile)
                self.socket_status = True
            except socket.error:
                return False      
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.connect((self.monitor_options['Host'], 
                    self.monitor_options['Port']))
                self.socket_status = True
            except socket.error:
                return False

    def _monitor_close(self):
        """Close the opened socket connection."""    
        if self.socket is not None:
            self.socket.close()

    def monitor_send(self, command, raw=True):
        """Send data to socket."""
        if raw:
            command = '%s\n' % command
        if self.socket_status:
            try:
                self.socket.send(command)
                time.sleep(0.2)
                return True
            except socket.error, error_msg:
                if error_msg[0] == 32:
                    print "Could not send data to socket."
                print error_msg[1]
                return False
        else:
            return False

    def monitor_recieve(self, socket_buffer=4098):
        """Recieve data from socket and return it as a list."""
        result = []
        no_result = ['No data available']
        if self.socket_status:
            data = self.socket.recv(socket_buffer)
            if len(data) == 0:
                return no_result
            data = data.split("\r\n")
            # have to do this check because second call does not send
            # the qemu info string
            if data[0].startswith("QEMU"):
                counter = self.recieve_data['data_offset_first_call']
                if len(data) > self.recieve_data['data_offset_first_call']:
                    while counter < len(data) - 1:
                        result.append(data[counter])
                        counter += 1
                    if len(result) == 0:
                        result = ["Done"]
                    return result
            else:                    
                counter = self.recieve_data['data_offset_second_call']
                if len(data) > self.recieve_data['data_offset_second_call']:
                    while counter < len(data)-1:
                        result.append(data[counter])
                        counter += 1
                    return result
        return no_result
