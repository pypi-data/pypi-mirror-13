#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2016 Canonical Ltd.  This software is licensed under the
# GNU Library General Public License version 3 (see the file LICENSE).
from setuptools import setup


setup(
    # metadata
    name='django-adminaudit',
    version='0.5',
    description="Extends Django's admin logging capabilities",
    url='https://launchpad.net/django-adminaudit',
    author='Ubuntu One Hackers',
    author_email='natalia.bidart@ubuntu.com',
    license='LGPLv3',
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    # content
    packages=[
        'adminaudit',
        'adminaudit.management',
        'adminaudit.management.commands',
        'adminaudit.migrations',
        'adminaudit.south_migrations',
    ],
    package_data={
        'adminaudit': [
            'templates/admin/adminaudit/auditlog/*.html',
            'templates/admin/*.html',
            'templates/adminaudit/*.txt',
        ],
    },
)
