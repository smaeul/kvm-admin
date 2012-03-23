#
# A collection of global functions.
#

"""
(c) 2012 jens Kasten <jens@kasten-edv.de>
"""

import os
from header import Header


def which(file_name):
    """Python implementation of linux which command."""
    if os.path.isfile(file_name) and os.access(file_name, os.X_OK):
        return file_name 
    for path in Header().search_paths:
        service = os.path.join(path, file_name)
        if os.path.isfile(service) and os.access(service, os.X_OK):
            return service
    return False

qemu_kvm_error_message = []
def qemu_kvm_error(self, message):
    """Just a collection of errors in a list."""
    qemu_kvm_error_message.append(message)   
