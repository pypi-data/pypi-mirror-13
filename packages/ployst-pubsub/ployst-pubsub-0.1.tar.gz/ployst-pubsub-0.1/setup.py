#!/usr/bin/env python
# # coding: utf-8
from setuptools import find_packages, setup


setup(
    name='ployst-pubsub',
    description='Client tool for the Google Cloud PubSub service',
    version='0.1',
    install_requires=[
        'google-api-python-client',
        'pycrypto',
    ],
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        ('License :: OSI Approved :: GNU Library or Lesser '
         'General Public License (LGPL)'),
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
