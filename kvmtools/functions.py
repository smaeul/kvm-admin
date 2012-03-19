#
# A collection of global functions.
#

"""
(c) 2012 jens Kasten <jens@kasten-edv.de>
"""

import sys


def which(file_name):
    """Python implementation of linux which command."""
    if os.path.isfile(file_name) and os.access(file_name, os.X_OK):
        return file_name 
    paths = ["/bin", "/sbin", "/usr/bin", "/usr/sbin", "/usr/local/sbin",
        "/usr/local/bin"]
    for path in paths:
        service = os.path.join(path, file_name)
        if os.path.isfile(service) and os.access(service, os.X_OK):
            return service
    return False
