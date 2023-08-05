#!/usr/bin/python
from setuptools import setup, find_packages

# Get the module version
from lsbinit import __version__

# Run the setup
setup(
    name             = 'lsbinit',
    version          = __version__,
    description      = 'Linux init scripts handler',
    long_description = open('DESCRIPTION.rst').read(),
    author           = 'David Taylor',
    author_email     = 'djtaylor13@gmail.com',
    url              = 'http://github.com/djtaylor/python-lsbinit',
    license          = 'GPLv3',
    packages         = find_packages(),
    keywords         = 'feedback terminal shell init service',
    classifiers      = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Terminals',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: Shells'
    ]
)