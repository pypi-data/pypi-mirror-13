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
# along with this program.  If not, see <http://www.gnu.org/licenses/

# Get values of the configuration file
'''Get values of the configuration file'''

import configparser
import sys

class ConfParse(object):
    '''ConfParse class'''
    def __init__(self, pathtoconf):
        '''Constructor of the ConfParse class'''
        self.consumer_key = ''
        self.consumer_secret = ''
        self.check_interval = 60
        self.pathtoconf = pathtoconf
        self.mailhost = ''
        self.mailfrom = ''
        self.mailto = ''
        self.main()

    def main(self):
        '''Main of the ConfParse class'''
        # read the configuration file
        config = configparser.ConfigParser()
        try:
            with open(self.pathtoconf) as conffile:
                config.read_file(conffile)
                section='twitter'
                if config.has_section(section):
                    self.consumer_key = config.get(section, 'consumer_key')
                    self.consumer_secret = config.get(section, 'consumer_secret')
                    self.access_token = config.get(section, 'access_token')
                    self.access_token_secret = config.get(section, 'access_token_secret')
                section='schedule'
                if config.has_section(section):
                    self.check_interval= config.get(section, 'check_interval')
                section='mail'
                if config.has_section(section):
                    self.mailhost = config.get(section, 'host')
                    self.mailfrom = config.get(section, 'from')
                    self.mailto = config.get(section, 'to')

        except (configparser.Error, IOError, OSError) as err:
            print(err)
            sys.exit(1)
        try:
            self.check_interval = int(self.check_interval)
        except ValueError as err:
            print(err)
            self.check_interval = 60

    @property
    def confvalues(self):
        '''get the values of the configuration file'''
        return {'consumer_key': self.consumer_key,
                'consumer_secret': self.consumer_secret,
                'access_token': self.access_token,
                'access_token_secret': self.access_token_secret,
                'check_interval': self.check_interval,
                'mailhost': self.mailhost,
                'mailfrom': self.mailfrom,
                'mailto': self.mailto}
