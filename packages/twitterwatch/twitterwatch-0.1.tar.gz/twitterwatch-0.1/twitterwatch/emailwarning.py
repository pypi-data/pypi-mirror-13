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

# EmailWarning class
'''EmailWarning class'''

import smtplib
from email.mime.text import MIMEText

class EmailWarning(object):
    '''EmailWarning class'''
    def __init__(self, cfgvalues, warning, user):
        '''Constructor of the EmailWarning class'''
        self.cfgvalues = cfgvalues
        self.warning = warning
        self.user = user
        self.main()

    def main(self):
        '''Main of the Main class'''
        try:
            msg = MIMEText(self.warning)
            msg['Subject'] = 'Twitter stream of {} has stopped'.format(self.user)
            msg['From'] = self.cfgvalues['mailfrom']
            msg['To'] = self.cfgvalues['mailto']
            s = smtplib.SMTP(self.cfgvalues['mailhost'])
            s.send_message(msg)
            s.quit()
        except smtplib.SMTPException as err:
            print('smtplib error: {}'.format(err))
