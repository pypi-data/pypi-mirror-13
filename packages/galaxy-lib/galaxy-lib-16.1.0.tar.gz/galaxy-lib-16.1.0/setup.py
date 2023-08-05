#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import os
import re
import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

SOURCE_DIR = "galaxy"

_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('%s/__init__.py' % SOURCE_DIR, 'rb') as f:
    init_contents = f.read().decode('utf-8')

    def get_var(var_name):
        pattern = re.compile(r'%s\s+=\s+(.*)' % var_name)
        match = pattern.search(init_contents).group(1)
        return str(ast.literal_eval(match))

    version = get_var("__version__")
    PROJECT_NAME = get_var("PROJECT_NAME")
    PROJECT_URL = get_var("PROJECT_URL")
    PROJECT_AUTHOR = get_var("PROJECT_AUTHOR")
    PROJECT_EMAIL = get_var("PROJECT_EMAIL")

TEST_DIR = 'tests'
PROJECT_DESCRIPTION = 'Subset of Galaxy (http://galaxyproject.org/) core code base designed to be used a library.'
PACKAGES = [
    'galaxy',
    'galaxy.jobs.metrics',
    'galaxy.jobs.metrics.collectl',
    'galaxy.jobs.metrics.instrumenters',
    'galaxy.objectstore',
    'galaxy.tools',
    'galaxy.tools.toolbox',
    'galaxy.tools.toolbox.filters',
    'galaxy.tools.toolbox.lineages',
    'galaxy.tools.linters',
    'galaxy.tools.deps',
    'galaxy.tools.deps.resolvers',
    'galaxy.util',
]
ENTRY_POINTS = '''
'''
PACKAGE_DATA = {
    'galaxy': [
        'util/docutils_template.txt',
    ],
}
PACKAGE_DIR = {
    SOURCE_DIR: SOURCE_DIR,
}

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

if os.path.exists("requirements.txt"):
    requirements = open("requirements.txt").read().split("\n")
else:
    # In tox, it will cover them anyway.
    requirements = []

# Only import cwltool for Python 2.7.
if sys.version_info[0] == 2 and sys.version_info[1] >= 7:
    requirements.append("cwltool")


test_requirements = [
    # TODO: put package test requirements here
]


setup(
    name=PROJECT_NAME,
    version=version,
    description=PROJECT_DESCRIPTION,
    long_description=readme + '\n\n' + history,
    author=PROJECT_AUTHOR,
    author_email=PROJECT_EMAIL,
    url=PROJECT_URL,
    packages=PACKAGES,
    entry_points=ENTRY_POINTS,
    package_data=PACKAGE_DATA,
    package_dir=PACKAGE_DIR,
    include_package_data=True,
    install_requires=requirements,
    license="AFL",
    zip_safe=False,
    keywords='galaxy',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: OSI Approved :: Academic Free License (AFL)',
        'Operating System :: POSIX',
        'Topic :: Software Development',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Testing',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite=TEST_DIR,
    tests_require=test_requirements
)
