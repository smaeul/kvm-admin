#
# build command to executing
#

"""
(c) 2011 Jens Kasten <jens@kasten-edv.de>
"""


class BuildCommand(object):
    """Build command"""
    
    def __init__(self):
        pass

    def build_command(self):
        """Return a tuple. First entry is a list to execute via subprocess
        and the second is a string to display it.
        """
        self.build_config()
        cmd_execute = []
        cmd_string = ""
        # Start to build a list, firstly add the qemu-kvm binary
        if "qemu-kvm" not in self.config:
            return (False, "Need qemu-kvm = /path/to/kvm option in config.")
        cmd_execute.append(self.config["qemu-kvm"])
        for key in self.exclude_options:
            if key in self.config:
                del self.config[key]
        # iterate over the user config and build a list
        for key, value in self.config.iteritems():
            # this check search for more option like -drive -drive etc.
            if "disabled" == value:
                continue
            elif isinstance(value, dict):
                for i in value.itervalues():
                    cmd_execute.append(''.join(['-', key]))
                    cmd_execute.append(i)
            elif "enabled" != value:
                # this qemu-kvm option have an option, so add -key value
                cmd_execute.append(''.join(['-', key]))
                cmd_execute.append(value)
            else:
                # this qemu-kvm option don't have any option 
                # so only add -key as argument
                cmd_execute.append(''.join(['-', key]))
        # build a string for to display on terminal output
        cmd_string = " ".join([value for value in cmd_execute])
        return (cmd_execute, cmd_string)


