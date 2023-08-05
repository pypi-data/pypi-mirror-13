# -*- coding: utf-8 -*-

import os
import sys
from setuptools import (setup, find_packages)
from django_cachekiller import __version__ as version

def fread(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-cachekiller',
    version=str(version),
    url='https://github.com/mgrp/django-cachekiller',
    download_url='https://github.com/mgrp/django-cachekiller/tarball/0.2',
    author='the m group, https://m.pr/',
    author_email='hi@m.pr',
    description=('Static file CDN cache buster for fast site updates.'),
    license='MIT',
    include_package_data=True,
    install_requires = ('django',),
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords = ['django', 'cache', 'buster', 'cdn', 'cachebuster'],
)

# eof
