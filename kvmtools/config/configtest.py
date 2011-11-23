#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Test for kvm guest config file
#

"""
(c) 2007-2011 Jens Kasten <jens@kasten-edv.de>
"""

import os
import argparse

from kvmtools.configparser import Parser


class TestConfig(object):
    """kvm guest test config parser"""
    
    def show_result(self, config_file):
        """Print the parsed config file."""
        if not os.path.isfile(config_file):
            print "Configfile does not exists: ", config_file
            return
        parser = Parser()
        result = parser(config_file)
        for key, value in result.iteritems():
            print "%s=%s" % (key, value)


def main():
    """commandline usage"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", metavar="kvm guest config file",
        help="Absolute path for kvm guest config file.")
    args = parser.parse_args()

    if not args.config:
        parser.print_usage()
        return
    config = TestConfig()
    config.show_result(args.config)


if __name__ == "__main__":
    main()
