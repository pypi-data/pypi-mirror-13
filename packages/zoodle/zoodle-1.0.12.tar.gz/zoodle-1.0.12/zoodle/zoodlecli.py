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

from requests import session
import jinja2
import datetime
from lxml import html
from argparse import ArgumentParser
import sys
import os
from configparser import RawConfigParser
import getpass

def parse_arguments():
    parser = ArgumentParser(
        description='Download class list from Moodle',
        epilog='(c) 2015 Peadar Grant'
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
    return vars(parser.parse_args())

def load_configuration(filename):
    config = RawConfigParser()
    config.read(filename)
    options = {}
    for key in config['default']:
        options[key]=config['default'][key]
    return options

def check_login_details(options):
    """
    Confirm that the username and password are available, prompting if required.
    """
    if options['username'] is None:
        options['username'] = input('Username: ')
    if options['password'] is None:
        options['password'] = getpass.getpass()
        
class Moodle:

    def __init__(self, baseurl, username, password):
        """
        Create a new moodle session with given credentials
        """
        self.baseurl = baseurl
        self.session = session()
        login_payload = {
            'username': username,
            'password': password,
        }
        self.session.post('%s/login/index.php' % baseurl, data=login_payload)

    def get_user_tree(self, courseid, groupid=None, roleid=None):
        """
        Return the HTML user tree of enrolled participants
        """
        search_params = {
            'id': courseid,
            'perpage': '10000'
            }
        if groupid is not None:
            search_params['filtergroup'] = groupid
        if roleid is not None:
            search_params['role'] = roleid
        response = self.session.get('%s/enrol/users.php' % ( self.baseurl ), params=search_params)
        return html.fromstring(response.content)
        
        
def main():

    options = parse_arguments()

    # Load configuration from file if requested
    if options['configfile'] is not None:
        config_options = load_configuration(options['configfile'])
        options.update(config_options)

    check_login_details(options)

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

if __name__=='__main__':
    main()
    
