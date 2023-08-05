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

# Send the tweet
'''Send the tweet'''

import tweepy

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from db2twitter.wasposted import WasPosted
from db2twitter.timetosend import TimeToSend

class TwSend(object):
    '''TwSend class'''
    def __init__(self, cfgvalues, tweets, session, dbvalues):
        '''Constructor for the TwBuild class'''
        _, self.lastinsertid, self.firstrun = dbvalues
        self.alreadysent = False
        self.cfgvalues = cfgvalues
        self.tweets = tweets
        # activate the twitter api
        self.auth = tweepy.OAuthHandler(self.cfgvalues['consumer_key'],
                                        self.cfgvalues['consumer_secret'])
        self.auth.secure = True
        self.auth.set_access_token(self.cfgvalues['access_token'],
                                    self.cfgvalues['access_token_secret'])
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        # activate the sqlite db
        self.session = session
        self.main()

    def main(self):
        '''main of TwSend class'''
        for tweet in self.tweets:
            self.alreadysent = False
            # store the tweets in the sqlite3 database
            self.storetweet(tweet)
            # if it is the first run, dont send all the tweets
            if not self.firstrun:
                tts = TimeToSend(self.cfgvalues)
                # are date and time ok to send the tweet?
                if tts.sendthetweet:
                    # was the tweet already sent?
                    if not self.alreadysent:
                        self.api.update_status(status=tweet)
                        #print(tweet)

    def storetweet(self, tweet):
        '''store a tweet in sqlite database'''
        newtweet = WasPosted(tweet=tweet, lastinsertid=self.lastinsertid)
        try:
            self.session.add(newtweet)
            self.session.commit()
        except (sqlalchemy.exc.IntegrityError) as err:
            print(err)
            print('tweet already sent')
            self.session.rollback()
            self.alreadysent = True
