#
# Module provide system information 
#

"""
(c) Jens Kasten <jens@kasten-edv.de>
"""

import os
import sys
from subprocess import Popen, PIPE


class System(object):

    def  __init__(self):
        self.kvm_pid = None

    def avail_memory(self):
        """Return available system memory in megabyte."""
        # TODO: proper way
        process1 = Popen(["free", "-m"], stdout=PIPE)
        process2 = Popen(["awk", "{print $4}"], stdin=process1.stdout, stdout=PIPE)
        result = process2.communicate()[0]
        mem = result.split("\n")
        return int(mem[1])

    def total_memory(self):
        """Return total amount of system memory in megabyte."""
        # TODO: proper way
        process1 = Popen(["free", "-m"], stdout=PIPE)
        process2 = Popen(["awk", "{print $2}"], stdin=process1.stdout, stdout=PIPE)
        result = process2.communicate()[0]
        mem = result.split("\n")
        return (mem[1])

    def get_cdrom(self):
        """Check if machine has a cdrom. Return the path to cdrom device."""
        if os.path.exists("/dev/cdrom"):
            return "/dev/cdrom"
        elif os.path.exists("/dev/dvd"):
            return "/dev/dvd"
        else:
            for i in range(0, 11):
                if os.path.exists("/dev/sr%d" % i):
                    return "/dev/sr%d" % i
        return None

    def get_pid(self):
        """Set pif if pidfile is available"""
        if os.path.isfile(self.kvm_pidfile):
            with open(self.kvm_pidfile) as fd:
                self.kvm_pid = int(fd.readline().strip())

    def _get_vnc(self):
        """Return vnc info."""
        self.monitor_send("info vnc")
        vnc = self.monitor_recieve()
        self.kvm_process_vnc = "\n".join(vnc)

    def _get_uuid(self):
        """Return the guest uuid."""
        self.monitor_send(self.qemu_monitor["uuid"])
        uuid = self.monitor_recieve()[0]
        self.kvm_process_uuid = uuid

    def _get_status(self):
        """Return the status from guest."""
        self.monitor_send(self.qemu_monitor["status"])
        status = self.monitor_recieve()[0]
        self.kvm_process_status = status

    def _get_process_info(self):
        """Collect information from proc."""
        with open(os.path.join("/proc", "%d/status" % self.kvm_pid)) as fd:
            lines = [line.strip().split(':') for line in fd.readlines()]
        for i in lines:
            name = "kvm_process_" + i[0].strip().lower()
            value = i[1].strip("\t").strip()
            setattr(self, name, value)

    def get_process_information(self):
        """Collect process information from different sources."""
        self._get_uuid()
        self._get_status()
        self._get_vnc()
        self._get_process_info()

    def is_running(self):
        """Check if the process is running by a given pid."""
        if self.kvm_pid:
            try:
                os.kill(self.kvm_pid, 0)
                return True
            except OSError:
                if os.path.isfile(self.kvm_pidfile):
                    os.remove(self.kvm_pidfile)
                if os.path.exists(self.kvm_socketfile):
                    os.remove(self.kvm_socketfile)
                return False
        else:
            process1 = Popen(['ps', 'ax'], stdout=PIPE, stderr=PIPE)
            search = "kvm_" + self.kvm_domain_name
            process2 = Popen(['grep', search], stdin=process1.stdout, 
                stdout=PIPE, stderr=PIPE)
            process1.stdout.flush()
            result = process2.communicate()
            status = result[0].split("\n")
            if len(status) > 2:
                pid = int(status[0].lstrip().split(" ")[0].strip())
                try:
                    os.kill(pid, 0)
                    self.kvm_pid = pid
                    return True
                except OSError:
                    if os.path.isfile(self.kvm_pidfile):
                        os.remove(self.kvm_pidfile)
                    if os.path.exists(self.kvm_socketfile):
                        os.remove(self.kvm_socketfile)
                    return False
            else:
                if os.path.isfile(self.kvm_pidfile):
                    os.remove(self.kvm_pidfile)
                if os.path.exists(self.kvm_socketfile):
                    os.remove(self.kvm_socketfile)
                return False  
