#!/usr/bin/env python3
# Class list query tool for Moodle
# Copyright (C) 2015 Peadar Grant
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
from argparse import ArgumentParser

from zoodle.commands import TestLoginCommand, UserListCommand

class Zoodle:

    def __init__(self):
        # following method from:
        # http://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html
        parser = ArgumentParser(
            description = "command-line moodle query tool",
            epilog = "(c) 2015 Peadar Grant",
            usage = """zoodle <command> [<args>]

subcommands:

testlogin  tests credentials can log into moodle
userlist   print all users on a course

---
"""
            )
        parser.add_argument('command', help='command to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print("unrecognized command")
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def testlogin(self):
        testLoginCommand = TestLoginCommand()
        testLoginCommand.main(sys.argv[2:])
        
    def userlist(self):
        userListCommand = UserListCommand()
        userListCommand.main(sys.argv[2:])
        
def main():
    zoodle = Zoodle()

if __name__=='__main__':
    main()

    
