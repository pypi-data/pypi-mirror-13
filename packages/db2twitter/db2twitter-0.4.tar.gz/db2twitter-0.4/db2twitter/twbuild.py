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

# Build the tweet to send
'''Build the tweet to send'''

class TwBuild(object):
    '''TwBuild class'''
    def __init__(self, cfgvalues, dbvalues):
        '''Constructor for the TwBuild class'''
        self.cfgvalues = cfgvalues
        self.dbvalues = dbvalues
        self.tweets = []
        self.main()

    def main(self):
        '''main of TwBuild class'''
        # get hashtags
        if self.cfgvalues['hashtags'] != '':
            hashtags = self.cfgvalues['hashtags'].split(',')
            hashtags = [i for i in hashtags if i != '']
        for i in self.dbvalues:
            j = self.cfgvalues['tweet'].format(*i)
            # identify and replace hashtags
            j = j.lower()
            for hashtag in hashtags:
                if ' {}'.format(hashtag) in j.lower():
                    j = j.replace(hashtag, '#{}'.format(hashtag))
            # uppercase for the first letter of the tweet
            if self.cfgvalues['upper_first_char']:
                j = j[0].upper() + j[1:]
            self.tweets.append(j)

    @property
    def readytotweet(self):
        '''return the tweet ready to be sent'''
        return self.tweets
