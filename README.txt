=========
kvm-tools
=========
A commandline script to use a simple guest configuration file.

usage: kvm-admin [-h]
                 domain_name
                 {boot,create,kill,migrate,modify,monitor,reboot,show,shutdown,status}
                 [option [option ...]]

optional arguments:
  -h, --help            show this help message and exit

QEMU-KVM domain:
  domain_name           Choose a KVM domain name, its the same like the
                        configuration file name

Action for a domain:
  {boot,create,kill,migrate,modify,monitor,reboot,show,shutdown,status}
                        Choose an action for the KVM guest

Monitor command:
  option                One ore more arguments can pass to the monitor.

usage: kvm-admin [-h] [--generate-options]
                 kvm_guest_name action [monitor [monitor ...]]

=========
Depencies
=========
List: python >=2.4 and < 3.0 
      python-argparse (debian package name)

All others are standard python library.

======
Update
======
When qemu-kvm change or add parameter, than the this run this command:
	generate-kvm-options --generate

# Fix: and a config with current qemu-kvm verion and compare it each run

This build a new list of all availables qemu-kvm options.
This is used to check if the given key in the configuration file 
is a valid qemu-kvm option.

====
Info
====
The qemu-kvm option for monitor, and pidfile has default values.
But this options can be overriden in each domain configuration file.

========
Downlaod
========
1. The scripts can downloaded via webrowser as bz2, zip, or gzip archive.
	http://hg.kasten-edv.de/kvm-tools
	https://hg.kasten-edv.de/kvm-tools --insecure

2. clone the mercurial repository. 
    hg clone http://hg.kasten-edv.de/kvm-tools  
    hg clone https://hg.kasten-edv.de/kvm-tools --insecure

============
Installation
============
Look at INSTALL.txt.
# Fix: debian package and new setup.py 

==================
System preparation
==================
Its recommend to use an unprivileged user.
It can set in the global configuration file /etc/kvm/config/kvm.cfg
Uncomment:
	# optional, add an user kvm to run the qemu-kvm process
	#runas = kvm

Each guest configuration file can have this option too.

Example to use a system user kvm on debian. If qemu-kvm is already installed, then add only the group kvm
and modify the /etc/passwd.

	addgroup --gid 116 kvm_test
	adduser --system --gid 116 --uid 116 --home /var/run/kvm_test --disabled-password --shell /bin/false kvm
	chown kvm:kvm /var/run/kvm or /usr/local/var/run/kvm
    	cmod 750 /var/run/kvm or /usr/local/var/run/kvm

=============
Kernel module
=============
If the kernel shipped by your distribution you have to load the follow kernel module.

kvm-module:
	modpobe -v kvm-[intel|amd]

For using tap device:
	modprobe -v tun

===================
Guest configuration
===================
An example for a domain(guest) configuration file.
The syntax values are 1:1 on commandline usage the only differ is instead using
	-option_name value
	option_name = value

Its exists only one tap option, which has an extend attribute.
This is only used in combination with tap device.
Its automatically add the tap device to given bridge.

The syntax to append to net = tap option is:
    Example:
	net = tap,bridge=bridge_name 

For fist run, you can use:
	kvm-admin my_new_domain create

This build a very minimalistic domain config through a console based dialog.
# Feature: build a python dialog script

Example domain configuration file:
    name = my_first_domain
    # first drive
    drive = file=/home/kvm/my_testfile.img,if=virtio,index=0,boot=on,cache=none
    # second drive 
    drive = file=/home/kvm/my_swapfile.img,if=virtio,index=1,cache=none
    # memory for using in the guest
    m = 512
    # default language for keyboard
    k = de
    # add more then one cpu to the guest
    smp = 2
    # vnc port 5901 on the qemu-kvm host machine
    # example usage: vncviever :1 
    vnc = :1
    # first network interface
    net = nic,mac=00:50:11:22:33:00
    net = tap,bridge=br0
    # second network interace 
    net = tap,bridge=br1
    net = nic,mac=00:50:11:22:33:01
    # to run kvm guest as unprivileged user
    runsas = kvm
    # override the pidfile, the directory have to writeable
    pidfile = absolute_path_to_pidfile
    # override the monitor to use tcp connection
    monitor = tcp:localhost:4444,server,nowait

Example kvm.cfg:
    # have to set the absolute path to qemu-kvm binary
    qemu-kvm = /usr/bin/kvm
    # optional, run the process in daemon mode
    daemonize = enabled
    # optional, use cpu typ 
    cpu = core2duo
    # optional, use localtime in guest
    rtc = base=localtime
    # optinal, run as kvm user
    runas = kvm

====================
Hotplug a pci device
====================
If you plan to hotplug a device in a guest this kernel module have to load in guest. 
	modprobe -v acpiphp
	modprobe -v pci_hotplug 

Use the monitor to hotplug a device:
    # add a nic to guest
    kvm-admin my_guest monitor pci_add auto nic model=e1000
    # add a harddrive to guest
    kvm-admin my_guest monitor pci_add auto storage file=/path/to/partion_or_file,if=virtio

=============
Monitor using
=============
You can communicate with the guest monitor on commandline.
Each command behind the monitor concatenate to a string. 
No quotations are needed.

usage: kvm-admin domain_name monitor help

Reboot or shutdown or status can send via the monitor too.
    kvm-admin domain_name monitor system_powerdown

You can use the command line monitor like the orgin "ALT + CTRL + 2" monitor.
You can add an usb device or ecject cdrom etc.
