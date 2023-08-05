# -*- coding: utf-8 -*-
# Copyright © 2015 Carl Chenet <carl.chenet@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

# Setup for Twitterwatch
'''Setup for Twitterwatch'''

import os.path

from setuptools import setup

CLASSIFIERS = [
    'Intended Audience :: End Users/Desktop',
    'Environment :: Console',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3.4'
]

setup(
    name='twitterwatch',
    version='0.1',
    license='GNU GPL v3',
    description='Twitter bot to watch a Twitter user timeline',
    long_description='Twitterwatch watches a user timeline in order to check if tweets are tweeted on a regular schedule.',
    classifiers=CLASSIFIERS,
    author='Carl Chenet',
    author_email='chaica@ohmytux.com',
    url='https://github.com/chaica/twitterwatch',
    download_url='https://github.com/chaica/twitterwatch',
    packages=['twitterwatch'],
    scripts=['scripts/twitterwatch'],
    install_requires=['tweepy>=3.3.0'],
)
