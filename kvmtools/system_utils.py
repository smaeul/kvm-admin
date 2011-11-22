#
# Module provide system information through the python-psutil
#

"""
(c) Jens Kasten <jens@kasten-edv.de>
"""

import os
import sys
try:
    import psutil
    required_version = [0, 1, 3]
    version = [int(i) for i in psutil.__version__.split(".")]
    for i in range(len(required_version)):
        if version[i] > required_version[i]:
            print "psutil in version %s is required" % required_version
            print "Installed version %s" % version
            sys.exit(1)
except ImportError, error_msg:
    print error_msg
    sys.exit(1)


class System(object):

    def avail_memory(self):
        """Return available system memory in megabyte."""
        memory = psutil.avail_phymem()
        return memory / (1024 * 1024)

    def total_memory(self):
        """Return total amount of system memory in megabyte."""
        memory = psutil.TOTAL_PHYMEM
        return memory / (1024 * 1024)

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

    def get_process_info(self, pid):
        """Return a disctionary about the process on given pid."""
        if not  self.is_running(pid):
            return False
        info = {}
        process = psutil.Process(pid)
        info["name"] = process.name
        info["uid"] = process.uid
        info["gid"] = process.gid
        rss, vms = process.get_memory_info()
        info["rss"] = rss / 1024
        info["vms"] = vms / 1024
        info["cmdline"] = process.cmdline
        #info["cpu_times"] = 
        return info

    def is_running(self, pid):
        if not type(pid) is int and psutil.pid_exits(pid):
            return False
        else:
            return True
