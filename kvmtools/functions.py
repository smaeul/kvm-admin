#
# A collection of global functions.
#

"""
(c) 2011 jens Kasten <jens@kasten-edv.de>
"""

import os
import sys
from subprocess import Popen, PIPE


def which(file_name):
    """Python implementation of which."""
    if os.path.isfile(file_name) and os.access(file_name, os.X_OK):
        return file_name 
    paths = ["/bin", "/sbin", "/usr/bin", "/usr/sbin", "/usr/local/sbin",
        "/usr/local/bin"]
    for path in paths:
        service = os.path.join(path, file_name)
        if os.path.isfile(service) and os.access(service, os.X_OK):
            return service
    return False

def get_pid_from_name(prog_name):
    """Return the pid."""
    try:
        process = Popen(["pgrep", prog_name], stdout=PIPE, stderr=PIPE)
        result = process.communicate()
        if len(result[1]) > 0:
            print result[1]
        else:
            if result[0] != "":
                temp = result[0].split("\n")
                if len(temp) > 3:
                    sys.exit("Need more specific program name.")
                else:
                    return int(temp[0])
    except OSError, e:
        sys.exit(e)
    except IOError, e:
        sys.exit(e)
