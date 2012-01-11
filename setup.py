# coding: utf-8
from distutils.core import setup
import json_diff

setup(
    name='json_diff',
    version='%s' % json_diff.__version__,
    description='Generates diff between two JSON files',
    author='Matěj Cepl',
    author_email='mcepl@redhat.com',
    url='https://fedorahosted.org/json_diff/',
    py_modules=['json_diff', 'test_json_diff', 'test_strings'],
    package_data={
        'json_diff': 'test/*'
    },
    long_description="""Compares two JSON files (http://json.org) and
generates a new JSON file with the result. Allows exclusion of some
keys from the comparison, or in other way to include only some keys.""",
    keywords=['json', 'diff'],
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
