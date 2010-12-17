#!/usr/bin/env python

"""
Handle all the monitor stuff.
"""

from os import path
from sys import exit
import socket
import time


class KvmMonitor(object):
    
    def __init__(self):
        # flag if socket can acces
        self.socket_status = False
        # data for method socket_recieve
        self.recieve_data = {
            "data_offset_start": 2, 
            "error_message": "No data from qemu monitor.",
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
        
    def _monitor_open(self):        
        """
        Open a socket to connect to the qemu-kvm monitor.
        """
        if path.exists(self.socketfile):
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                self.socket.connect(self.socketfile)
                self.socket_status = True
                return True
            except socket.error:
                return False      
        else:
            return False

    def _monitor_close(self):
        """
        Close the socket. 
        """    
        self.socket.close()

    def monitor_send(self, command):
        """
        Send data to socket.
        """
        if self.socket_status:
            self.socket.send(command + "\n")
            time.sleep(0.2)
            return True
        else:
            return False

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
                counter = self.recieve_data['data_offset_start']
                if len(data) > self.recieve_data['data_offset_start']:
                    while counter < len(data)-1:
                        result.append(data[counter])
                        counter += 1
                    return result
            else:                    
                counter = self.recieve_data['data_offset_start']-1
                if len(data) > self.recieve_data['data_offset_start']-1:
                    while counter < len(data)-1:
                        result.append(data[counter])
                        counter += 1
                    return result
                    
        else:
            return False 
            

def main():
    mon = KvmMonitor()
    if len(sys.argv) == 2:
        mon.socketfile = sys.argv[1]            
    else:
        print "usage: %s socketfile" % sys.argv[0]
        sys.exit()
    if mon.monitor_open():
        msg = "info status" 
        mon.monitor_send(msg)
        print mon.monitor_recieve()
        mon.monitor_close()

if __name__ == "__main__":
    import sys
    main()
            
