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

'''Was this tweet posted before'''

# external library imports
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# retweet library imports
from retweet.senttweets import SentTweets


class TweetWasPosted:
    '''Was this tweet posted before'''
    def __init__(self, cfgvalues):
        '''Constructor of the TweetWasPosted'''
        self.cfgvalues = cfgvalues
        # activate the sqlite db
        engine = create_engine('sqlite:///{}'.format(self.cfgvalues['sqlitepath']))
        tmpsession = sessionmaker(bind=engine)
        session = tmpsession()
        self.session = session
        SentTweets.metadata.create_all(engine)
        self.allsenttweetids=[]
        for twid in self.session.query(SentTweets.id).all():
            self.allsenttweetids.append(twid.id)

    def wasposted(self, tweet):
        '''Was this tweet posted already'''
        if tweet in self.allsenttweetids:
            return True
        else:
            return False

    def storetweet(self, tweettostore):
        '''Store the last sent tweet'''
        lastsenttweet = SentTweets(id=tweettostore)
        try:
            self.session.add(lastsenttweet)
            self.session.commit()
        except (sqlalchemy.exc.IntegrityError) as err:
            print(err)
            print('tweet already posted')
