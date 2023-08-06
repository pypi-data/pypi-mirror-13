from zoodle.moodle import Moodle, CredentialsError
from zoodle.command import Command

class CheckLoginCommand(Command):
    def __init__(self):
        super(CheckLoginCommand, self).__init__()

    @classmethod
    def help_text(cls):
        return "confirm credentials can access moodle"

    def main(self, args):

        self.initialise_options(args)
        options = self.options

        try:
            Moodle(options['baseurl'], options['username'], options['password'])
            print("credentials OK")
        except CredentialsError:
            print("credentials incorrect")
        
