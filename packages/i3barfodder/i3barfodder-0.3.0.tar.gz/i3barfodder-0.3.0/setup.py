from setuptools import setup
from i3barfodder import constants
import os

setup(
    name = constants.PROJECTNAME,
    version = constants.VERSION,
    license = 'GPLv3+',
    author = 'Random User',
    author_email = 'rndusr@posteo.de',
    url = 'https://gitlab.com/rndusr/i3barfodder',
    description = 'Powerful i3bar status line generator',
    keywords = 'i3 i3bar',

    install_requires = ['psutil>=2.2.1',
                        'pyinotify>=0.9.5',
                        'python-dateutil>=2.4.2'],

    packages = ['i3barfodder', 'i3bfutils'],
    entry_points = { 'console_scripts': [ 'i3bf = i3barfodder.main:run' ] },
    scripts = ['workers/'+script for script in os.listdir('workers/')
                if script.startswith('i3bf-')],

    classifiers = [
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Topic :: System :: Monitoring',
        'Programming Language :: Python :: 3.4',
    ]
)
