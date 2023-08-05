import datetime
import os

import jinja2

from zoodle.command import Command
from zoodle.moodle import Moodle

class UserListCommand(Command):
    def __init__(self):
        pass

    @classmethod
    def help_text(cls):
        return "query and template user list for course"
    
    def parse_arguments(self, args):
        parser = self.argument_parser()
        parser.add_argument('courseid', help='course ID number (from URL, not course code)')
        parser.add_argument('-T', '--template', help='template name', default="list.txt")
        parser.add_argument('-t', '--title', help='title (usage depends on template)', default='Class list')
        parser.add_argument('--groupid', help='group ID number to filter by', default=None)
        parser.add_argument('--roleid', help='role ID number to filter by', default=None)
        parser.add_argument('--templatedir', help='template directory', default=None)
        return vars(parser.parse_args(args))

    def main(self, args):

        options = self.parse_arguments(args)

        # Load configuration from file if requested
        if options['configfile'] is not None:
            config_options = self.load_configuration(options['configfile'])
            options.update(config_options)

        self.check_login_details(options)

        moodle = Moodle(options['baseurl'], options['username'], options['password'])
        tree = moodle.get_user_tree(options['courseid'], options['groupid'], options['roleid'])

        # Get all students enrolled
        students = tree.xpath("//tr[@class='userinforow']/td[@class='field col_userdetails cell c0']/div[@class='subfield subfield_userfullnamedisplay']/text()")

        # Template setup
        this_dir = os.path.split(__file__)[0]
        if options['templatedir'] is not None:
            templates_dir = options['templatedir']
        else:
            templates_dir = os.path.join(this_dir, 'templates')
        loader = jinja2.FileSystemLoader(templates_dir)
        environment = jinja2.Environment(loader=loader)
        template = environment.get_template(options['template'])
        template_vars = {
            "course": tree.xpath("//h1/text()")[0],
            "code": tree.xpath("(//ul[@class='breadcrumb']/li/a)[2]/text()")[0],
            "title": options['title'],
            "timestamp": datetime.date.today().strftime("%B %d, %Y"),
            "students": students,
            "number_of_students": len(students),
            "group": tree.xpath("//select[@id='id_filtergroup']/option[@selected='selected']/text()")[0],
            "role": tree.xpath("//select[@name='role']/option[@selected='selected']/text()")[0],
        }

        # Send template to output
        print(template.render(template_vars))
