#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'pybuilder_aws_plugin',
          version = '151',
          description = '''PyBuilder plugin to handle AWS functionality''',
          long_description = '''''',
          author = "Valentin Haenel, Stefan Neben",
          author_email = "valentin@haenel.co, stefan.neben@gmail.com",
          license = 'Apache',
          url = 'https://github.com/ImmobilienScout24/pybuilder_aws_plugin',
          scripts = [],
          packages = ['pybuilder_aws_plugin'],
          py_modules = [],
          classifiers = ['Development Status :: 2 - Pre-Alpha', 'Environment :: Console', 'Intended Audience :: Developers', 'Intended Audience :: System Administrators', 'License :: OSI Approved :: Apache Software License', 'Programming Language :: Python', 'Operating System :: POSIX :: Linux', 'Topic :: System :: Software Distribution', 'Topic :: System :: Systems Administration', 'Topic :: System :: Archiving :: Packaging', 'Topic :: Utilities'],
          entry_points={
          'console_scripts':
              []
          },
             #  data files
             # package data
          install_requires = [ "boto3", "cfn-sphere>=0.1.21", "httpretty<=0.8.10" ],
          
          zip_safe=True
    )
