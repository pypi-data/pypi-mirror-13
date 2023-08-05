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

# standard library imports
import configparser
import sys

class ConfParse(object):
    '''ConfParse class'''
    def __init__(self, pathtoconf):
        '''Constructor of the ConfParse class'''
        self.user_to_retweet = 'journaldupirate'
        self.consumer_key = ''
        self.consumer_secret = ''
        access_token = ''
        self.access_token_secret = ''
        self.pathtoconf = pathtoconf
        self.dontretweethashes = []
        self.onlyiftags = []
        self.olderthan = 0
        self.youngerthan = 0
        self.main()

    def main(self):
        '''Main of the ConfParse class'''
        # read the configuration file
        config = configparser.ConfigParser()
        try:
            with open(self.pathtoconf) as conffile:
                config.read_file(conffile)
                if config.has_section('main'):
                    self.user_to_retweet = config.get('main', 'screen_name_of_the_user_to_retweet')
                    self.consumer_key = config.get('main', 'consumer_key')
                    self.consumer_secret = config.get('main', 'consumer_secret')
                    self.access_token = config.get('main', 'access_token')
                    self.access_token_secret = config.get('main', 'access_token_secret')
                    self.retweets = config.get('main', 'retweets')
                    self.waitminsecs = config.get('main', 'waitminsecs')
                    self.waitmaxsecs = config.get('main', 'waitmaxsecs')
                    if config.has_option('main', 'do_not_retweet_hashtags'):
                        dontretweethashes = config.get('main', 'do_not_retweet_hashtags')
                        if dontretweethashes:
                            hashes = [i for i in dontretweethashes.split(',') if i != '']
                            self.dontretweethashes = hashes
                    if config.has_option('main', 'only_if_hashtags'):
                        onlyiftags = config.get('main', 'only_if_hashtags')
                        if onlyiftags:
                            hashtags = [i for i in onlyiftags.split(',') if i != '']
                            self.onlyiftags = hashtags
                    if config.has_option('main', 'older_than'):
                        self.olderthan = config.get('main', 'older_than')
                    if config.has_option('main', 'younger_than'):
                        self.youngerthan = config.get('main', 'younger_than')
                if config.has_section('sqlite'):
                    self.sqlitepath = config.get('sqlite', 'sqlitepath')

        except (configparser.Error, IOError, OSError) as err:
            print(err)
            sys.exit(1)
        try:
            self.retweets = int(self.retweets)
        except ValueError as err:
            print(err)
            self.retweets = 0
        try:
            self.waitminsecs = int(self.waitminsecs)
        except ValueError as err:
            print(err)
            self.waitminsecs = 60
        try:
            self.waitmaxsecs = int(self.waitmaxsecs)
        except ValueError as err:
            print(err)
            self.waitmaxsecs = 600
        try:
            self.olderthan = int(self.olderthan)
        except ValueError as err:
            print(err)
            self.olderthan = 0
        try:
            self.youngerthan = int(self.youngerthan)
        except ValueError as err:
            print(err)
            self.youngerthan = 0

    @property
    def confvalues(self):
        '''get the values of the configuration file'''
        return {'user_to_retweet':  self.user_to_retweet,
                'consumer_key': self.consumer_key,
                'consumer_secret': self.consumer_secret,
                'access_token': self.access_token,
                'access_token_secret': self.access_token_secret,
                'retweets': self.retweets,
                'waitminsecs': self.waitminsecs,
                'waitmaxsecs': self.waitmaxsecs,
                'sqlitepath': self.sqlitepath,
                'dontretweethashes': self.dontretweethashes,
                'onlyifhashtags': self.onlyiftags,
                'olderthan': self.olderthan,
                'youngerthan': self.youngerthan}
