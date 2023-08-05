#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from setuptools import Command
import codecs
import os

# http://fgimian.github.io/blog/2014/04/27/running-nose-tests-with-plugins-using-the-python-setuptools-test-command/
# Inspired by the example at https://pytest.org/latest/goodpractises.html
class NoseTestCommand(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Run nose ensuring that argv simulates running nosetests directly
        import nose
        nose.run_exit(argv=['nosetests'])

class GenerateLexicalParserCommand(Command):
    user_options = []

    def initialize_options(self):
        """Abstract method that is required to be overwritten"""

    def finalize_options(self):
        """Abstract method that is required to be overwritten"""

    def run(self):
        print(" => Generate lexical parser with wisent...")
        os.system("grammar\wisent\wisent.py  -o binmapper\parser\grammar.py grammar/binmapper.wi")
        
        
def read_file(filename):
   """
   Read a utf8 encoded text file and return its contents.
   """
   with codecs.open(filename, 'r', 'utf8') as f:
       return f.read()
       
setup(
    name     = 'binmapper',
    version  = '0.1a4',
    packages = find_packages(),
    install_requires=[
          'jinja2',
      ],
    description  = 'Domain Specific Language(DSL) for parsing and mapping binary data to python objects',
    long_description = read_file('README.md'), 
    author       = 'RedSkotina',
    author_email = 'red.skotina@gmail.com',
    url          = 'https://bitbucket.org/RedSkotina/binmapper',
    download_url = 'https://bitbucket.org/RedSkotina/binmapper/downloads',
    license      = read_file('LICENSE.txt'),
    keywords     = ['dsl','parser','binary','mapper'],
    classifiers  = [
        'Intended Audience :: Developers',
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='nose.collector',
    tests_require=['nose','coverage',],
    cmdclass={
        'test': NoseTestCommand,
        'generate': GenerateLexicalParserCommand},
    zip_safe = False,
    include_package_data=True,  # use MANIFEST.in during install
    package_data = {
            '': ['binmapper/parser/templates/*.template'],
            }
    
)