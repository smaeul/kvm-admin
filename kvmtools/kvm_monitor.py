#!/usr/bin/env python

"""
Handle all the monitor stuff.
"""

from os import path
from sys import exit
import socket
import time


class KvmMonitor(object):
    """
    Class for connect and disconnect to a qemu monitor socket.
    Additional send data to and recieve data from monitor.
    """

    def __init__(self, monitor):
        self._monitor = monitor
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
        try:
            self._monitor_open()
        except:
            pass

    def __del__(self):
        try:
            self.monitor_close()
        except:
            pass

    #########################################
    # monitor via unix socket or tcp socket #
    #########################################
    def _monitor_open(self):        
        """
        Open a socket to connect to the qemu-kvm monitor.
        """
        # Fix: raise a error message if connection fail
        if self._monitor['Type'] == 'unix': 
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                self.socket.connect(self.socketfile)
                self.socket_status = True
            except socket.error:
                return False      
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.connect((self._monitor['Host'], self._monitor['Port']))
                self.socket_status = True
            except socket.error:
                return False

    def _monitor_close(self):
        """
        Close the socket. 
        """    
        self.socket.close()

    def monitor_send(self, command, raw=True):
        """
        Send data to socket.
        """
        if raw:
            command = '%s\n' % command
        if self.socket_status:
            self.socket.send(command)
            time.sleep(0.2)

    def monitor_recieve(self, buffer=4098):
        """
        Recieve data from socket and return a list.
        """
        result = []
        if self.socket_status:
            data = self.socket.recv(buffer)
            data = data.split("\r\n")
            # have to do this check because second call does not send
            # the qemu info string
            if data[0].startswith("QEMU"):
                counter = self.recieve_data['data_offset_first_call']
                if len(data) > self.recieve_data['data_offset_first_call']:
                    while counter < len(data)-1:
                        result.append(data[counter])
                        counter += 1
                    return result
            else:                    
                counter = self.recieve_data['data_offset_second_call']
                if len(data) > self.recieve_data['data_offset_second_call']:
                    while counter < len(data)-1:
                        result.append(data[counter])
                        counter += 1
                    return result
        else:
            return ['No data available.'] 
            

def main():
    pass


if __name__ == "__main__":
    main()
            
