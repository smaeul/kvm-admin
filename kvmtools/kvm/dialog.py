#

"""
(c) 2011 Jens Kasten <jens@kasten-edv.de>
"""

import sys
try:
    import curses
except ImportError, error_msg:
    print error_msg
    sys.exit(1)


class KvmDialog(object):

    def __init__(self):
        self.dialog = curses.initscr()
        self.dialog.border(0)
        self.dialog.addstr(12, 26, "python curses")
        self.dialog.refresh()
        self.a = self.dialog.getch()
        curses.endwin()

d = KvmDialog()
print d.a

