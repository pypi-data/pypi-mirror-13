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

Configuration file
------------------

Using the command switch

::

   --configfile config.ini

you can instead specify any of the required command-line options in the file:

::

   [default]
   baseurl=base.url
   username=your.username
   password=your.password

Obviously, if you're storing passwords, you should chmod the file as appropriate.

Group filtering
---------------

You can filter groups by using the groupid command switch, as in the example:

::

   --groupid 3859

Note that the group ID is the group's **id number**, NOT the group name.
You can determine this by doing a manual filter in the usual way and noting the filtergroup URL parameter.

The default templates will display the group's name when this option is used.
