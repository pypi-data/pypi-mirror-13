import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

__name__ = 'smache'
__version__ = '0.0.3'
__author__ = 'Anders Emil Nielsen'
__author_email__ = 'aemilnielsen@gmail.com'
__doc__ = """
Lots of description
"""

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()


class ToxTestCommand(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        sys.exit(os.system('tox'))

setup(
    name=__name__,
    version=__version__,
    author=__author__,
    license='MIT',
    description=__doc__,
    keywords='smart caching dataflow reactive push-based',
    long_description=read_md('README.md'),
    install_requires=[
        'redis',
    ],
    tests_require=['tox'],
    url='http://limecode.dk',
    cmdclass={'test': ToxTestCommand}
)

