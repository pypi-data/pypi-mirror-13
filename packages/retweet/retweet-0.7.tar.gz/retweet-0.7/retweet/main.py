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
import os.path
import sys
import tweepy

from retweet.cliparse import CliParse
from retweet.confparse import ConfParse
from retweet.tweetwasposted import TweetWasPosted
from retweet.validate import Validate
from retweet.waitamoment import WaitAMoment


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
        self.twp = TweetWasPosted(self.cfgvalues)

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
        lasttweets = self.api.user_timeline(self.cfgvalues['user_to_retweet'])
        # see if the last tweet of twitter api was sent already
        lasttweetid = lasttweets[-1].id
        # extract the last 20 tweet ids
        lasttweetids = [tweet.id for tweet in lasttweets]
        lasttweetids.reverse()
        tweetstosend = []
        # test if the last 20 tweets were posted
        for lasttweet in lasttweetids:
            if not self.twp.wasposted(lasttweet):
                Validate(self.cfgvalues, self.api, lasttweet)
        sys.exit(0)
