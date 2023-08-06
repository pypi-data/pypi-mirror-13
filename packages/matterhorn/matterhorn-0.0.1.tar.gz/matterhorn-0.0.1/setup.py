#!/usr/bin/env python

from setuptools import setup

setup(
    name='matterhorn',
    version='0.0.1',
    description='Integration Framework for Mattermost',
    author='Jasper Schulz',
    author_email='jasper.b.schulz@gmail.com',
    packages=['matterhorn'],

    install_requires=[
        "Flask==0.10.1",
        "requests==2.9.1"
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
    ]
 )