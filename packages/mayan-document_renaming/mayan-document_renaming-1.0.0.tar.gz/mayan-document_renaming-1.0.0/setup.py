#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

with open('README.rst') as f:
    readme = f.read()
with open('HISTORY.rst') as f:
    history = f.read()
with open('LICENSE') as f:
    license = f.read()

setup(
    author='Roberto Rosario',
    author_email='roberto.rosario@mayan-edms.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
    description='Automatic document renaming app for Mayan EDMS.',
    include_package_data=True,
    license=license,
    long_description=readme + '\n\n' + history,
    name='mayan-document_renaming',
    package_data={'': ['LICENSE']},
    package_dir={'document_renaming': 'document_renaming'},
    packages=[
        'document_renaming', 'document_renaming.migrations',
        'document_renaming.tests'
    ],
    platforms=['any'],
    url='https://gitlab.com/mayan-edms/document_renaming',
    version='1.0.0',
    zip_safe=False,
)
