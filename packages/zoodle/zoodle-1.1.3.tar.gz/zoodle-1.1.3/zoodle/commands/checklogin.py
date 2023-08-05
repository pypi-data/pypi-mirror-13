from zoodle.moodle import Moodle, CredentialsError
from zoodle.command import Command

class CheckLoginCommand(Command):
    def __init__(self):
        pass

    @classmethod
    def help_text(cls):
        return "confirm credentials can access moodle"

    def parse_arguments(self, args):
        return vars(self.argument_parser().parse_args(args))

    def main(self, args):
        options = self.parse_arguments(args)

        # Load configuration from file if requested
        if options['configfile'] is not None:
            config_options = self.load_configuration(options['configfile'])
            options.update(config_options)

        self.check_login_details(options)

        try:
            Moodle(options['baseurl'], options['username'], options['password'])
            print("credentials OK")
        except CredentialsError:
            print("credentials incorrect")
        
