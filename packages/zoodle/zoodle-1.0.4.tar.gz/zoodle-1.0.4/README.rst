Zoodle - command-line query tool for Moodle
===========================================

Zoodle is a command-line query tool for the Moodle LMS that queries
class lists on a remote moodle server from the command line.

Installing zoodle
-----------------

Zoodle is a pure python package, but runs only on Python 3.5.
Pip is required.

::

    pip install zoodle

Alternatively you can clone the source and install zoodle using

::

    setup.py install

It will make the necessary script link so that zoodle can be run from
the command line.

Using Zoodle
------------

To run zoodle, type:

::

    zoodle --username=<your_username> --password=<your_password> --baseurl=https://your.moodle <course_id> <template_name>

More information about the command-line parameters

-  Base URL can be determined by looking at your login page's URL. If
   your login page is https://your.moodle/login/index.php, the --baseurl
   should be set to https://your.moodle without the trailing slash.
-  course\_id is the numerical course ID that can be found in the
   location bar when viewing the main page of your chosen course.
-  Your username and password are those used normally to login to
   Moodle. They are saved to command history when used on the command
   line so be careful on shared computers.
-  There are two available templates in the templates directory as
   shipped: classlist.txt and signinsheet.txt

This command will then output all enrolled users on the course to the
stdout.
