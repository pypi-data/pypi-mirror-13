from argparse import ArgumentParser
from configparser import RawConfigParser
import getpass
import abc

class Command:
    """
    Superclass for commands called from CLI dispatcher
    """

    __metaclass__ = abc.ABCMeta

    @classmethod
    def help_text(cls):
        return "base command"

    def argument_parser(self):
        parser = ArgumentParser(
            epilog='(c) 2015 Peadar Grant',
            )
        parser.description = self.help_text()
        parser.add_argument('-c', '--configfile', help='config file to load', default=None)
        parser.add_argument('-b', '--baseurl', help='base URL')
        parser.add_argument('-u', '--username', help='username (will prompt if not supplied)')
        parser.add_argument('-p', '--password', help='password (will prompt if not supplied)')
        return parser

    def load_configuration(self, filename):
        """
        Loads configuration from file
        """
        config = RawConfigParser()
        config.read(filename)
        options = {}
        for key in config['default']:
            options[key] = config['default'][key]
        return options    

    def check_login_details(self, options):
        """
        Confirm that the username and password are available, prompting if required.
        """
        if options['baseurl'] is None:
            options['baseurl'] = input('Base URL: ')
        if options['username'] is None:
            options['username'] = input('Username: ')
        if options['password'] is None:
            options['password'] = getpass.getpass()
