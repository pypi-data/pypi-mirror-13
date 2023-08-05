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

# CLI parsing
'''CLI parsing'''

import os.path
import sys

class CliParse(object):
    '''CliParse class'''
    def __init__(self):
        '''Constructor for the CliParse class'''
        self.pathtoconf = sys.argv[-1]
        if len(sys.argv) >  2 and sys.argv[-2] == 'circle':
            self.iscircling = True
        else:
            self.iscircling = False
        self.cliargs = {}
        self.main()

    def main(self):
        '''main of CliParse class'''
        # checks for the path to the configuration
        if self.pathtoconf.endswith('db2twitter.py') or self.pathtoconf.endswith('db2twitter'):
            print('No config file was provided. Exiting.')
            sys.exit(0)
        if not os.path.exists(self.pathtoconf):
            print('the path you provided for db2twitter configuration file does not exists')
            sys.exit(1)
        if not os.path.isfile(self.pathtoconf):
            print('the path you provided for db2twitter configuration is not a file')
            sys.exit(1)
        self.cliargs['validpathtoconf'] = self.pathtoconf
        self.cliargs['iscircling'] = self.iscircling

    @property
    def args(self):
        '''return the cli arguments'''
        return self.cliargs
