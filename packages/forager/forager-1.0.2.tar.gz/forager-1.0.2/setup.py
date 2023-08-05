#!/usr/bin/env python
from distutils.core import setup
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)


setup(
    name='forager',
    version='1.0.2',
    description='A utility for finding feeds on websites',
    author='Rick Petithory',
    author_email='rick@curata.com',
    url='https://github.com/CurataEng/forager',
    license='GNU General Public License v3.0',
    packages=['forager'],
    package_dir={'forager': 'forager'},
    install_requires=[
        'beautifulsoup4==4.4.1',
        'requests==2.9.1',
        'future==0.15.2',
    ],
    classifiers = [
        'Programming Language :: Python',
    ],
    tests_require=['tox', 'mock'],
    cmdclass = {'test': Tox},
)
