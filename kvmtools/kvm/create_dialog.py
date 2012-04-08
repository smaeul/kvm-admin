#
# Module to create an initial kvm-admin domain configuration file
#

"""
(c) 2011-2012 Jens Kasten <jens@kasten-edv.de>
"""


class CreateDialogConsole(object):
    """Console dialog to create inital config file."""

    def __init__(self):
        self.fd = None    
        self._is_cdrom = False

    def create_dialog(self):
        """Methode to create a dialog for creating a domain config"""
        try:
            # If the write somehow failed, it could lead to an endless loop
            self.fd = open(self.kvm_domain_file, "w")
            self._write(self.name_input())
            self._write(self.memory_input())
            self._write(self.cdrom_input())
            if self._is_cdrom:
                self._write(self.boot_order_input())
            self._write(self.drive_input())
        except IOError, e:
            RuntimeError("Operation failed: %s, %s" % e.message, 
                self.kvm_domain_file)
        finally:
            if self.fd:
                self.fd.close()
    
    def _write(self, content):
        self.fd.write(content + "\n")

    def name_input(self):
        name = raw_input("Name [%s]: " % self.kvm_domain_name)
        if len(name) == 0:
            return "# name of window title (name)\nname = %s" % self.kvm_domain_name
        else:
            return "# name of window title (name)\nname = %s" % name

    def memory_input(self):         
        comment = "# system memory in megabyte (m)\n"
        print "Total memory of the machine: %s" % self.total_memory()
        while True:
            memory = raw_input("Memory in MB [%d]: " % 128)
            if len(memory) == 0 or memory == "q":
                return comment + "m = 128"
            try:
                memory = int(memory)
                if memory > self.total_memory():
                    print "Machine has not that much memory %sMB." % \
                        self.avail_memory()
                    accept = raw_input("Should this value used? [Y/n]:").lower()
                    if len(accept) == 0 or accept == "y":
                        return comment + "m = %d" % memory
                elif memory > self.avail_memory():
                    print "Memory in the moment available %sMB." % \
                        self.avail_memory()
                    accept = raw_input("Should this value used? [Y/n]:").lower()
                    if len(accept) == 0 or accept == "y":
                        return comment + "m = %d" % memory
                else:
                    return comment + "m = %d" % memory
            except ValueError:
                print "Memory must give as a positive digit or press enter."
                    
    def cdrom_input(self):                    
        cdrom = raw_input("Would you like use a cdrom [Y/n]: ").lower()
        if len(cdrom) == 0 or cdrom == "y":
            if self.get_cdrom():
                cdrom_path = raw_input("Path to cdrom device [%s]: " \
                    % self.get_cdrom())
                # use default cdrom which was found
                self._is_cdrom = True
                if len(cdrom_path) == 0:
                    return "# path to cdrom (cdrom)\ncdrom = %s" % self.get_cdrom()
                else:
                    return "# path to cdrom (cdrom)\ncdrom = %s" % cdrom_path
            else:
                print "No default cdrom available."
                while True:
                    cdrom_path = raw_input("Path to iso image: ")
                    if len(cdrom_path) == 0:
                        print "Type q to continue."
                    elif cdrom_path == "q":
                        return "" 
                    else:
                        self._is_cdrom = True
                        return "# path to iso image\ncdrom = %s" % cdrom_path
        return ""

    def boot_order_input(self):
        print "\tIs for fresh installation a good order 'cd'."
        print "\tBecause if not a bootable harddrive availablen"
        print "\tthan is booting from installation cdrom."
        print "\tAfter successfully installation its booting after reboot in correct order."
        boot = raw_input("Would you like to boot the qemu-kvm guest from cdrom? [Y/n]")
        while True:
            if boot.lower() == "y" or len(boot) == 0:
                return "# boot order: first cdrom and second harddrive\nboot = cd"
            else:
               return "# boot order: first harddrive, no other option\nboot = c"
        return ""

    def drive_input(self):
        drives = {}
        while True:
            print "Available qemu-kvm device driver [ide,scsi,virtio]."
            print "Type q to continue without harddrive."
            driver = raw_input("default qemu-kvm device driver [virtio]: ")
            if driver == "q":
                return ""
            if driver in ["ide", "scsi", "virtio"]:
                break
            elif len(driver) == 0:
                driver = "virtio"
                break
        while True:
            print "Type q to quit."
            drive_amount = raw_input("How many harddrives you are like to use [1]: ")
            try:
                if drive_amount == "q":
                   return "" 
                elif len(drive_amount) == 0:
                    drive_amount = 1
                    break
                else:
                    drive_amount = int(drive_amount)
                    if drive_amount > 4:
                        print "Its initial configuration. Max 4 devices cat set."
                    else:
                        break
            except ValueError:
                print "Amount of drive must a positive digit greater the null."
                print "Type q to continue without harddrive."
        while True:
            for i in range(1, drive_amount + 1):
                while True:
                    drive = raw_input("Path to hardrive %d: " % i)
                    if len(drive) > 0:
                        drives[i] = {
                            "file": drive, 
                            "if": driver, 
                            "index": i-1,
                            "boot": "off",
                            "cache": "none",
                            "media": "disk",
                        }
                        break
            break
        while True:
            if len(drives) > 1:
                print  "From which device should boot: "
            if len(drives) == 1:
                drives[1]["boot"] = "on"
                break
            else:
                for key in drives.iterkeys():
                    print "[%d] %s" % (key, drives[key]["file"])
                boot = raw_input("Index: ")
                if boot == "q":
                     break
            try:
                boot = int(boot)
                drives[boot]["boot"] = "on"
                break
            except ValueError:
                print "Index have to a digit from list above."
                print "Type q to continue without set boot on for a harddrive."
            except KeyError:
                print "Index not in list."
        drive_list = ["# harddive (drive)"]
        for key, value in drives.iteritems():
            to_write = "drive = file=%s,index=%d,if=%s,media=%s,cache=%s,boot=%s" % \
               (value["file"], value["index"], value["if"], value["media"], 
                value["cache"], value["boot"])
            drive_list.append(to_write)
        return "\n".join(drive_list)

