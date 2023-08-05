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
import os.path
import sys

class ConfParse(object):
    '''ConfParse class'''
    def __init__(self, pathtoconf):
        '''Constructor of the ConfParse class'''
        self.rows = {}
        self.ids = {}
        self.sqlfilter = {}
        self.pathtoconf = pathtoconf
        self.main()

    def main(self):
        '''Main of the ConfParse class'''
        # read the configuration file
        config = configparser.ConfigParser()
        try:
            with open(self.pathtoconf) as conffile:
                config.read_file(conffile)
                if config.has_section('twitter'):
                    self.consumer_key = config.get('twitter', 'consumer_key')
                    self.consumer_secret = config.get('twitter', 'consumer_secret')
                    self.access_token = config.get('twitter', 'access_token')
                    self.access_token_secret = config.get('twitter', 'access_token_secret')
                    self.tweet = config.get('twitter', 'tweet')
                    self.hashtags = config.get('twitter', 'hashtags')
                    self.upper_first_char = config.getboolean('twitter', 'upper_first_char')
                if config.has_section('database'):
                    self.dbconnector = config.get('database', 'dbconnector')
                    self.dbhost = config.get('database', 'dbhost')
                    self.database = config.get('database', 'database')
                    self.dbuser = config.get('database', 'dbuser')
                    self.dbpass = config.get('database', 'dbpass')
                    self.dbtables = config.get('database', 'dbtables')
                if config.has_section('timer'):
                    self.days = config.get('timer', 'days')
                    self.hours = config.get('timer', 'hours')
            
                    alltables = self.dbtables.split(',')
                    alltables = (i for i in alltables if i !='')
                    for table in alltables:
                        if config.has_option('database', '{}_rows'.format(table)):
                            rows = config.get('database', '{}_rows'.format(table)).split(',')
                            rows = [i for i in rows if i != '']
                            self.rows[table] = rows
                        if config.has_option('database', '{}_id'.format(table)):
                            self.ids[table] = config.get('database', '{}_id'.format(table))
                        if config.has_option('database', '{}_sqlfilter'.format(table)):
                            self.sqlfilter[table] = config.get('database', '{}_sqlfilter'.format(table))
                if config.has_section('sqlite'):
                    self.sqlitepath = config.get('sqlite', 'sqlitepath')
                if config.has_section('circle'):
                    self.twlastnb = config.get('circle', 'last_tweets')
                    self.twbatchnb = config.get('circle', 'each_time')
        except (configparser.Error, IOError, OSError) as err:
            print(err)
            sys.exit(1)

    @property
    def confvalues(self):
        '''get the values of the configuration file'''
        return {'consumer_key': self.consumer_key,
                'consumer_secret': self.consumer_secret,
                'access_token': self.access_token,
                'access_token_secret': self.access_token_secret,
                'tweet': self.tweet,
                'hashtags': self.hashtags,
                'upper_first_char': self.upper_first_char,
                'dbconnector': self.dbconnector,
                'dbhost': self.dbhost,
                'database': self.database,
                'dbuser': self.dbuser,
                'dbpass': self.dbpass,
                'dbtables': self.dbtables,
                'rows': self.rows,
                'ids': self.ids,
                'sqlfilter': self.sqlfilter,
                'sqlitepath': self.sqlitepath,
                'days': self.days,
                'hours': self.hours,
                'circlelasttwnb': self.twlastnb,
                'circletwbatchnb': self.twbatchnb}
