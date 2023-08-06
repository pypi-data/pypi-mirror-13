from zoodle.moodle import Moodle
from zoodle.command import Command

class CoursesCommand(Command):
    def __init__(self):
        super(CoursesCommand, self).__init__()

    @classmethod
    def help_text(cls):
        return "list all accessible courses"
    
    def main(self, args):
        
        self.initialise_options(args)
        options = self.options

        moodle = Moodle(options['baseurl'], options['username'], options['password'])        
        courses = moodle.available_courses()
        for course in courses:
            print(course)
