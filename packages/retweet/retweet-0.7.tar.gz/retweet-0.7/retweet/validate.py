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

# Validate class
'''Validate class'''

import os.path
import sys
import tweepy

from retweet.tweetwasposted import TweetWasPosted
from retweet.waitamoment import WaitAMoment


class Validate(object):
    '''Validate class'''
    def __init__(self, cfgvalues, api, tweet):
        '''send the tweet'''
        self.cfgvalues = cfgvalues
        self.api = api
        self.twp = TweetWasPosted(self.cfgvalues)
        try:
            # test if it was retweeted enough to be retweeted by me
            if len(self.api.retweets(tweet)) >= self.cfgvalues['retweets']:
                # send the tweet if all checks are ok
                if not self.notretweethashes(tweet) and self.retweetonlyifhashtags(tweet):
                    self.api.retweet(tweet)
                    #print("tweet {} sent!".format(tweet))
        except (tweepy.error.TweepError) as err:
            print("{}".format(err))
            print("the tweet is probably retweeted already. Twitter does not allow to retweet 2 times")
        finally:
            # now store the tweet
            if not self.twp.wasposted(tweet):
                self.twp.storetweet(tweet)
                WaitAMoment(self.cfgvalues['waitminsecs'], self.cfgvalues['waitmaxsecs'])

    def notretweethashes(self, tweet):
        '''check if the tweet has a hash for not retweeting'''
        found = False
        # check if the current tweet contains a do-not-retweet hash
        for i in self.cfgvalues['dontretweethashes']:
            if '#{}'.format(i) in self.api.get_status(tweet).text:
                found = True
        return found

    def retweetonlyifhashtags(self, tweet):
        '''retweet only if the tweet has the following hashtag'''
        found = False
        if self.cfgvalues['onlyifhashtags']:
            # check if the current tweet contains one of the hashtags to be retweeted
            for i in self.cfgvalues['onlyifhashtags']:
                if '#{}'.format(i) in self.api.get_status(tweet).text:
                    found = True
        else:
            found = True
        return found
