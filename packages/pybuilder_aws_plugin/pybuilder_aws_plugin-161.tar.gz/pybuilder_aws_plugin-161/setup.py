#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'pybuilder_aws_plugin',
        version = '161',
        description = '''PyBuilder plugin to handle AWS functionality''',
        long_description = '''''',
        author = "Valentin Haenel, Stefan Neben",
        author_email = "valentin@haenel.co, stefan.neben@gmail.com",
        license = 'Apache',
        url = 'https://github.com/ImmobilienScout24/pybuilder_aws_plugin',
        scripts = [],
        packages = ['pybuilder_aws_plugin'],
        py_modules = [],
        classifiers = [
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Operating System :: POSIX :: Linux',
            'Topic :: System :: Software Distribution',
            'Topic :: System :: Systems Administration',
            'Topic :: System :: Archiving :: Packaging',
            'Topic :: Utilities'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [
            'boto3',
            'cfn-sphere>=0.1.21',
            'httpretty'
        ],
        dependency_links = [],
        zip_safe=True,
        cmdclass={'install': install},
    )
