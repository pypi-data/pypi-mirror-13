#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import oscar_telegrambot

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = oscar_telegrambot.__version__

if sys.argv[-1] == 'publish':
    try:
        import wheel
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-oscar-telegram-bot',
    version="0.1.1",
    description="""Telegram Bot for Oscar shops""",
    long_description=readme + '\n\n' + history,
    author='Juan Madurga',
    author_email='jlmadurga@gmail.com',
    url='https://github.com/jlmadurga/django-oscar-telegram-bot',
    packages=[
        'oscar_telegrambot',
    ],
    include_package_data=True,
    install_requires=[
        'django-oscar==1.1.1',
        'django-telegram-bot==0.1.1'
    ],
    license="BSD",
    zip_safe=False,
    keywords='django-oscar-telegram-bot',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',        
    ],
)
