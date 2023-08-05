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

from zoodle.commands.checklogin import CheckLoginCommand
from zoodle.commands.userlist import UserListCommand
from zoodle.commands.courses import CoursesCommand

def main():
    """
    main command dispatcher
    """
    # Supported commands
    available_commands = {
        "courses": CoursesCommand,
        "userlist": UserListCommand,
        "checklogin": CheckLoginCommand,
        }

    # Build explanation string for help display
    command_explanation = ""
    for command in available_commands:
        command_explanation = ( command_explanation +
                                "  " +
                                command.ljust(12) +
                                available_commands[command].help_text()
                                + "\n" )
    # following method from:
    # http://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html
    parser = ArgumentParser(
        usage=""" zoodle <command> [<args>]
available commands:

%s

help on individual commands: zoodle <command> -h

""" % command_explanation)
    parser.add_argument('command', help='command to run')
    args = parser.parse_args(sys.argv[1:2])
    if args.command not in available_commands:
        print("unrecognized command")
        parser.print_help()
        exit(1)

    command = available_commands[args.command]()
    command.main(sys.argv[2:])

if __name__ == '__main__':
    main()
