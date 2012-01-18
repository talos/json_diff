# coding: utf-8
from distutils.core import setup, Command
import os.path
import json_diff


class RunTests(Command):
    """New setup.py command to run all tests for the package.
    """
    description = "run all tests for the package"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import unittest
        import test.test_json_diff
        unittest.TextTestRunner(verbosity=2).run(test.test_json_diff.suite)


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return "\n" + f.read().replace("\r\n", "\n")


def get_long_description():
    return read("README.txt") \
        + "\nChangelog:\n" + "=" * 10 + "\n" \
        + read("NEWS.txt")

setup(
    name='json_diff',
    version='%s' % json_diff.__version__,
    description='Generates diff between two JSON files',
    author='Matěj Cepl',
    author_email='mcepl@redhat.com',
    url='https://fedorahosted.org/json_diff/',
    py_modules=['json_diff'],
    long_description=get_long_description(),
    keywords=['json', 'diff'],
    cmdclass={'test': RunTests},
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
        ]
)
