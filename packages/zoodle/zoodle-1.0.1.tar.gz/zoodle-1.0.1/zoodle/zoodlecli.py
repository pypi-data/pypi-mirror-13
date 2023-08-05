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

def parse_arguments():
    parser = ArgumentParser(
        description='Download class list from Moodle',
        epilog='(c) 2015 Peadar Grant'
        )
    parser.add_argument('courseid', help='course ID number (from URL, not course code)')
    parser.add_argument('template', help='template name')
    parser.add_argument('--title', help='title (usage depends on template)', default='Class list')
    parser.add_argument('--baseurl', help='base URL')
    parser.add_argument('--username', help='username')
    parser.add_argument('--password', help='password')
    return vars(parser.parse_args())

if __name__=='__main__':

    options = parse_arguments()
    
    # Login to Moodle and request student list from Module
    login_payload = {
        'username': options['username'],
        'password': options['password'],
    }
    with session() as c:
        c.post('%s/login/index.php' % options['baseurl'], data=login_payload)
        response = c.get('%s/enrol/users.php?id=%s&perpage=10000' % ( options['baseurl'], options['courseid'] ))
        tree = html.fromstring(response.content)

    # Get all students enrolled
    students = tree.xpath("//tr[@class='userinforow']/td[@class='field col_userdetails cell c0']/div[@class='subfield subfield_userfullnamedisplay']/text()")

    # Template setup
    this_dir, this_filename = os.path.split(__file__)
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
    }

    # Send template to output
    print(template.render(template_vars))

