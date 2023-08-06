# setup for zoodle

from setuptools import setup, find_packages
from codecs import open
from os import path

setup(
    name='zoodle',
    version='1.1.7',
    description='command-line Moodle query tool',
    long_description='command-line Moodle query tool',
    url='https://github.com/peadargrant/zoodle',
    author='Peadar Grant',
    author_email='peadargrant@gmail.com',
    license='GPLv3+',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='moodle',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['jinja2', 'lxml', 'requests'],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    package_data={
        'zoodle': ['commands/templates/*.txt'],
    },
    entry_points={
        'console_scripts': [
            'zoodle=zoodle.zoodle:main',
        ],
    },
)
