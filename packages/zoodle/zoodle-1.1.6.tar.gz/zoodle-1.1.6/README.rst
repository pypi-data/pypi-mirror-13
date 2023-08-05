Zoodle - command-line query tool for Moodle
===========================================

Zoodle is a command-line query tool for the Moodle LMS that queries
class lists on a remote moodle server from the command line.

What can Zoodle be used for?
----------------------------

Zoodle was originally designed to pull student lists from Moodle in a way that could be automated and/or scheduled.
In other words, I needed a utility that could be invoked from cron and pull down the current student list from Moodle each morning, rendering it as plaintext and sending it to the print spooler. 
The included templates are all plaintext, however since the templating is done using Jinja2, rendering the student list as HTML would be straightforward.
Furthermore, using Apache FOP or LaTeX would allow for PDF generation. 

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

Zoodle functions like the git command, where a single wrapper runs a number of possible subcommands.
To list them just type:

::

   zoodle --help


Credential check
----------------

Before using Zoodle, you should verify that your credentials can login, by running:

::

   zoodle checklogin -u <your_username> -b https://your.moodle 

-  Base URL can be determined by looking at your login page's URL. If
   your login page is https://your.moodle/login/index.php, the --baseurl
   should be set to https://your.moodle without the trailing slash.
-  Your username and password are those used normally to login to
   Moodle.
-  Username and Password will be asked for, or can be supplied with the -u/-username and/or -p/--password options.
   If supplying passwords on the command line, be aware that they probably will remain in your command-line history.
- For scripting purposes, you can disable any prompting with the -n/--noninteractive argument. This will cause missing parameters to raise an error.

   
Class list report
-----------------

Zoodle's main feature is the class list report, which can be invoked as follows:

::

    zoodle userlist -u <your_username> -baseurl https://your.moodle <course_id>

More information about the command-line parameters

-  course\_id is the numerical course ID that can be found in the
   location bar when viewing the main page of your chosen course.
-  By default, the list of names is printed direct to the screen. There are two additional available templates in the templates directory as shipped: classlist.txt and signinsheet.txt, using jinja2.

This command will then output all enrolled users on the course to the
stdout.

Configuration file
------------------

Using the command switch

::

   --configfile config.ini

you can instead specify any of the baseurl, username or password options in the file:

::

   [DEFAULT]
   baseurl=base.url
   username=your.username
   password=your.password

Obviously, if you're storing passwords, you should chmod the file as appropriate.

Multiple profiles can be stored using the --profile switch to select the desired one, which may be useful if you teach in multiple colleges or use separate moodle servers.
The DEFAULT profile (if present) will be used to "fill in" any parameters that are not specified in the others.

::

   [DEFAULT]
   baseurl=base.url
   username=your.username
   password=your.password

   [training]
   baseurl=trainingserver.base.url
   
   [other.college.cz]
   baseurl=other.base.url
   username=other.username
   password=other.password


In the above example, the base URL would be overridden in [training] but would inherit the username/password.
The [other.college.cz] section overrides all.

Filtering by group and/or role
------------------------------

You can filter by group and/or role by using the groupid/roleid command switch, as in the example:

::

   --groupid 3859 --roleid 5

Note that the group ID is the group/role's **id number**, NOT the corresponding name.
You can determine this by doing a manual filter in the usual way and noting the filtergroup or role URL parameter.

The default templates will display the group's name when this option is used.

Custom templates
----------------

Zoodle supports custom templates using the Jinja2 templating engine.
To use custom templates, use the --templatesdir option to point to your own directory:

::

   --templatesdir my_templates

The templates included with the application give a reasonable starting point for further customisation.

Contributions
-------------

Contributions are most welcome by way of pull requests.
