"""
Command abstract class
"""

from argparse import ArgumentParser
from configparser import RawConfigParser
import getpass
import abc

def load_configuration(filename, profile):
    """
    Loads configuration from file
    """
    config = RawConfigParser()
    config.read(filename)
    options = {}
    for key in ['baseurl', 'username', 'password']:
        options[key] = config[profile].get(key)
    return options


class Command:
    """
    Superclass for commands called from CLI dispatcher
    """

    __metaclass__ = abc.ABCMeta

    @classmethod
    def help_text(cls):
        """
        Help text printed for arg parser and command list
        """
        return "base command"

    def __init__(self):
        self.options = None
        self.parser = ArgumentParser(
            epilog='(c) 2015 Peadar Grant',
            )
        self.parser.description = self.help_text()
        self.parser.add_argument('-c', '--configfile', help='config file to load', default=None)
        self.parser.add_argument('-P', '--profile', help='configuration profile', default='DEFAULT')
        self.parser.add_argument('-b', '--baseurl', help='base URL (will prompt if not supplied)')
        self.parser.add_argument('-u', '--username', help='username (will prompt if not supplied)')
        self.parser.add_argument('-p', '--password', help='password (will prompt if not supplied)')
        self.parser.add_argument('-n', '--noninteractive', help='disables all keyboard prompts',
                                 default=False, action='store_true')

    def initialise_options(self, args):
        """
        Initialises options from args, config file and by prompting
        """
        self.options = vars(self.parser.parse_args(args))

        # fill in from config file
        if self.options['configfile'] is not None:
            config_options = load_configuration(self.options['configfile'], self.options['profile'])
            self.options.update(config_options)

        # prompt for missing options
        for parameter in ['baseurl', 'username', 'password']:
            if self.options[parameter] is None:
                if self.options['noninteractive']:
                    raise ValueError("missing %s parameter" % parameter)
                if parameter == 'password':
                    self.options[parameter] = getpass.getpass()
                else:
                    self.options[parameter] = input('%s: ' % parameter)

