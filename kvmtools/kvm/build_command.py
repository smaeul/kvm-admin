#
# build command to executing
#

"""
(c) 2011 Jens Kasten <jens@kasten-edv.de>
"""

from kvmtools.kvm.build_config import BuildConfig


class BuildCommand(BuildConfig):
    """Build command"""
    
    def __init__(self):
        BuildConfig.__init__(self)
        self.commmand = ()

    def build_command(self):
        """Create a tuple command. 
        First entry is a list that is executed via subprocess
        and the second is a string to display the command.
        """
        self.build_config()
        if self.config is None:
            return None 
        cmd_execute = []
        cmd_string = ""
        # Start to build a list
        # first add the qemu-kvm binary path
        cmd_execute.append(self.config["qemu-kvm"])
        # delete the helper parameter from config
        for key in self.exclude_options:
            if key in self.config:
                del self.config[key]
        # iterate over the config and build a list
        for key, value in self.config.iteritems():
            # ignore disabled values
            if self.is_disabled == value:
                continue
            # this check search for more option like -drive -drive etc.
            elif isinstance(value, dict):
                for i in value.itervalues():
                    cmd_execute.append(''.join(['-', key]))
                    cmd_execute.append(i)
            elif self.is_enabled != value:
                # this qemu-kvm option have an option, so add -key value
                cmd_execute.append(''.join(['-', key]))
                cmd_execute.append(value)
            else:
                # this qemu-kvm option don't have any option 
                # so only add -key as argument
                cmd_execute.append(''.join(['-', key]))
        # build a string for to display on terminal output
        cmd_string = " ".join([value for value in cmd_execute])
        self.command = (cmd_execute, cmd_string)
