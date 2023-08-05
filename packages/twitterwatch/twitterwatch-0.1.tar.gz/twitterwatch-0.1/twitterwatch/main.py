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

# Main class
'''Main class'''

import configparser
import datetime
import os.path
import sys
import tweepy

from twitterwatch.cliparse import CliParse
from twitterwatch.confparse import ConfParse
from twitterwatch.emailwarning import EmailWarning

class Main(object):
    '''Main class'''
    def __init__(self):
        '''Constructor of the Main class'''
        # parse the command line
        rtargs = CliParse()
        pathtoconf = rtargs.configfile
        # read the configuration file
        cfgparse = ConfParse(pathtoconf)
        self.cfgvalues = cfgparse.confvalues

        # activate the twitter api
        self.auth = tweepy.OAuthHandler(self.cfgvalues['consumer_key'],
                                        self.cfgvalues['consumer_secret'])
        self.auth.secure = True
        self.auth.set_access_token(self.cfgvalues['access_token'],
                                    self.cfgvalues['access_token_secret'])
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.main()

    def main(self):
        '''Main of the Main class'''
        # get the 20 last tweets
        lasttweets = self.api.user_timeline()
        # see if the last tweet of twitter api was sent already
        lasttweet = lasttweets[0]
        # find the date of the last tweet
        lastactiondate = lasttweet.created_at
        # get the current date
        currentdate = datetime.datetime.now()
        # get the interval between two checks
        pause = datetime.timedelta(minutes=self.cfgvalues['check_interval'])
        if (currentdate - pause) > lastactiondate:
            user = self.api.me().screen_name
            # warn
            warning = 'Twitter stream of {} has stopped since {}'.format(user, lastactiondate.strftime("%d/%m/%Y - %H:%M:%S")) 
            emailwarn = EmailWarning(self.cfgvalues, warning, user)
            print(warning)
