import datetime
from argparse import ArgumentParser
import sys
import os
from configparser import RawConfigParser
import getpass

import jinja2

from zoodle.moodle import Moodle, CredentialsError

class Command:

    def load_configuration(self, filename):
        """
        Loads configuration from file
        """
        config = RawConfigParser()
        config.read(filename)
        options = {}
        for key in config['default']:
            options[key]=config['default'][key]
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
    

class TestLoginCommand(Command):
    def __init__(self):
        pass

    def parse_arguments(self, args):
        parser = ArgumentParser(
            description='check moodle credentials',
            epilog='(c) 2015 Peadar Grant',
            )
        parser.add_argument('-c', '--configfile', help='config file to load', default=None)
        parser.add_argument('-b', '--baseurl', help='base URL')
        parser.add_argument('-u', '--username', help='username (will prompt if not supplied)')
        parser.add_argument('-p', '--password', help='password (will prompt if not supplied)')
        return vars(parser.parse_args(args))

    def main(self, args):
        options = self.parse_arguments(args)

        # Load configuration from file if requested
        if options['configfile'] is not None:
            config_options = load_configuration(options['configfile'])
            options.update(config_options)

        self.check_login_details(options)

        try:
            moodle = Moodle(options['baseurl'], options['username'], options['password'])
            print("credentials OK")
        except CredentialsError:
            print("credentials incorrect")
        

class UserListCommand(Command):
    def __init__(self):
        pass
    
    def parse_arguments(self, args):
        parser = ArgumentParser(
            description='Download class list from Moodle',
            epilog='(c) 2015 Peadar Grant',
        )
        parser.add_argument('courseid', help='course ID number (from URL, not course code)')
        parser.add_argument('template', help='template name')
        parser.add_argument('-t', '--title', help='title (usage depends on template)', default='Class list')
        parser.add_argument('-c', '--configfile', help='config file to load', default=None)
        parser.add_argument('-b', '--baseurl', help='base URL')
        parser.add_argument('-u', '--username', help='username (will prompt if not supplied)')
        parser.add_argument('-p', '--password', help='password (will prompt if not supplied)')
        parser.add_argument('--groupid', help='group ID number to filter by', default=None)
        parser.add_argument('--roleid', help='role ID number to filter by', default=None)
        parser.add_argument('--templatedir', help='template directory', default=None)
        return vars(parser.parse_args(args))

    def main(self, args):

        options = self.parse_arguments(args)

        # Load configuration from file if requested
        if options['configfile'] is not None:
            config_options = load_configuration(options['configfile'])
            options.update(config_options)

        self.check_login_details(options)

        moodle = Moodle(options['baseurl'], options['username'], options['password'])
        tree = moodle.get_user_tree(options['courseid'], options['groupid'], options['roleid'])

        # Get all students enrolled
        students = tree.xpath("//tr[@class='userinforow']/td[@class='field col_userdetails cell c0']/div[@class='subfield subfield_userfullnamedisplay']/text()")

        # Template setup
        this_dir, this_filename = os.path.split(__file__)
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
