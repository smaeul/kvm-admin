#
# Module to create an initial kvm-admin domain configuration file
#

"""
(c) 2011 Jens Kasten <jens@kasten-edv.de>
"""


class CreateDialogConsole(object):
    """Console dialog to create inital config file."""
    
    def create_dialog(self, open_type="r"):
        """Methode to create a dialog for creating a domain config"""
        with open(self.kvm_domain_file, open_type) as _fd:
            name = raw_input("Name [%s]: " % self.kvm_domain_name)
            if len(name) == 0:
                _fd.write("name = %s\n" % self.kvm_domain_name)
            else:
                _fd.write("name = %s\n" % name)
            # set memory 
            print ("Total memory of the machine: %d" % \
            self.total_memory())
            while True:
                memory = raw_input("Memory in MB [%d]: " % 128)
                if len(memory) == 0:
                    _fd.write("m = 128\t\t\t# system memory in megabyte\n")
                    break
                if memory == "q":
                    break
                try:
                    memory = int(memory)
                    if memory > self.total_memory():
                        print ("Machine has not enough total memory %d." % \
                            self.avail_memory())
                        accept = raw_input("Should this value used? [Y/n]:").lower()
                        if len(accept) == 0 or accept == "y":
                            _fd.write("m = %d\t\t\t# system memory in megabyte\n" % \
                                memory)
                            break
                   
                    elif memory > self.avail_memory():
                        print ("Machine has not enough available memory %d." % \
                            self.avail_memory())
                        accept = raw_input("Should this value used? [Y/n]:").lower()
                        if len(accept) == 0 or accept == "y":
                            _fd.write("m = %d\t# system memory in megabyte\n" % \
                                memory)
                            break
                    else:
                        _fd.write("m = %d\t# system memory in megabyte\n" % \
                            memory)
                        break
                except ValueError:
                    print ("Memory must give as a positive digit or type q to contiue.")
            # set cdrom
            is_cdrom = False
            cdrom = raw_input("Would you like use a cdrom [Y/n]: ").lower()
            if len(cdrom) == 0 or cdrom == "y":
                if self.get_cdrom():
                    cdrom_path = raw_input("Path to cdrom device [%s] press just enter or path to image: " \
                        % self.get_cdrom())
                else:
                    print ("Could not found cdrom device.")
                    while True:
                        cdrom_path = raw_input("Path to iso image: ")
                        if len(cdrom_path) == 0:
                            print "Type q to continue."
                        elif cdrom_path == "q" or len(cdrom_path) > 0:
                            break
                while True:
                    if cdrom_path == "q":
                        break
                    if len(cdrom_path) == 0:
                        is_cdrom = True
                        cdrom_device = self.get_cdrom()
                        if self.get_cdrom():
                            _fd.write("cdrom = %s\t# path to cdrom or iso image\n" % \
                                self.get_cdrom())
                            break
                        else:
                            break
                    else:
                        is_cdrom = True
                        _fd.write("cdrom = %s\t# path to cdrom or iso image\n" % cdrom_path)
                        break
                if is_cdrom:
                    boot = raw_input("Would you like to boot the qemu-kvm guest from cdrom? [Y/n]")
                    while True:
                        if boot.lower() == "y" or len(boot) == 0:
                            _fd.write("boot = cd\t# boot order harddrive and if not bootable then cdrom.\n")
                            break
                        else:
                            _fd.write("boot = c\t# boot order harddrive and if not bootable then cdrom.\n")
                            break
            # set drive
            drives = {}
            while True:
                print ("Available qemu-kvm device driver [ide,scsi,virtio].")
                print ("Type q to continue without harddrive.")
                driver = raw_input("default qemu-kvm device driver [virtio]: ")
                if driver == "q":
                    break
                if driver in ["ide", "scsi", "virtio"]:
                    break
                elif len(driver) == 0:
                    driver = "virtio"
                    break
            while True:
                if driver == "q":
                    break
                drive_amount = raw_input("How many harddrives you are like to use [1]: ")
                try:
                    if drive_amount == "q":
                        break
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
                    print ("Amount of drive must a positive digit greater the null.")
                    print ("Type q to continue without harddrive.")
            while True:
                if driver == "q":
                    break
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
            if len(drives) > 1:
                print ("From which device should boot: ")
            while True:
                if driver == "q":
                    break
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
            for key, value in drives.iteritems():
                to_write = "drive = file=%s,index=%d,media=%s,cache=%s,boot=%s" % \
                    (value["file"], value["index"], value["media"], 
                     value["cache"], value["boot"])
                _fd.write(to_write + "\n")
