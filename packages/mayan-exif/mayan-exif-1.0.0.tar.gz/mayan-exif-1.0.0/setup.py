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
    description='EXIF data extraction app for Mayan EDMS.',
    include_package_data=True,
    install_requires=('sh==1.11',),
    license=license,
    long_description=readme + '\n\n' + history,
    name='mayan-exif',
    package_data={'': ['LICENSE']},
    package_dir={'exif': 'exif'},
    packages=['exif', 'exif.backends', 'exif.migrations', 'exif.tests'],
    platforms=['any'],
    url='https://gitlab.com/mayan-edms/exif',
    version='1.0.0',
    zip_safe=False,
)
