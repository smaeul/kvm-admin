#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Testcase for configparser.
(c) 2007-20010 Jens Kasten <igraltist@rsbac.org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import os
import sys
import getopt

from configparser import Parser


class TestParser(object):

    def help(self):
        print """ 
-c | --config  # its need the absolut path to the config wich should testet.
-h | --help    # print this help
        """
        sys.exit()

    def usage(self):
        print "usage: %s -c 'configfile' or [--help|-h]" % sys.argv[0]
        sys.exit()

    def arguments(self):
        """
        It take a configfile and print the output 'key = value' from configparser.
        """
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hc:", ["help", "config"])
        except getopt.GetoptError:
            self.usage()

        if len(opts) == 1:
            if opts[0][0] in ("-c", "--config"):
                config_to_parse = opts[0][1]
                if not os.path.isfile(config_to_parse):
                    print "Error, '%s' not exists" % config_to_parse
                    sys.exit()
                else:
                    return config_to_parse
            else:
                if opts[0][0] in ("-h, --help"):
                    self.help()
                else:
                    self.usage()
        else:
            self.usage()


def main():
    tester = TestParser()
    config = tester.arguments()
    parser = Parser()
    result = parser(config)
    for key,value in result.iteritems():
        print "%s=%s" % (key, value)

if __name__ == "__main__":
    main()

# vim: tabstop=4 expandtab shiftwidth=4
