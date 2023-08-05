from zoodle.moodle import Moodle, CredentialsError
from zoodle.command import Command

class CoursesCommand(Command):
    def __init__(self):
        pass

    @classmethod
    def help_text(cls):
        return "list all accessible courses"
    
    def parse_arguments(self, args):
        return vars(self.argument_parser().parse_args(args))
    
    def main(self, args):
        options = self.parse_arguments(args)

        if options['configfile'] is not None:
            config_options = self.load_configuration(options['configfile'])
            options.update(config_options)

        self.check_login_details(options)
        moodle = Moodle(options['baseurl'], options['username'], options['password'])        
        courses = moodle.available_courses()
        for course in courses:
            print(course)
