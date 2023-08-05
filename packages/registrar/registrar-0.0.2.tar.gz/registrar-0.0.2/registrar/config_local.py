# -*- coding: utf-8 -*-
# -----------------------
# Copyright 2015 Halfmoon Labs, Inc.
# All Rights Reserved
# -----------------------

'''
    local configuration file
'''

import os

DEBUG = True

#BLOCKSTORED_IP = '54.197.247.244'
#BLOCKSTORED_IP = '54.82.121.156'
#BLOCKSTORED_IP = '172.30.1.199'

email_regrex = '@yopmail.com'

#MONGODB_URI = os.environ['MONGODB_URI']
#OLD_DB = os.environ['OLD_DB']
#AWSDB_URI = os.environ['AWSDB_URI']
#MONGOLAB_URI = os.environ['MONGOLAB_URI']

MAIN_SERVER = 'localhost'
LOAD_SERVERS = []
MAX_PENDING_TX = 50

#FRONTEND_SECRET = os.environ['FRONTEND_SECRET']

CHAIN_API_KEY = 'e21be6b69908544615b1d00f2c333c13'

SERVER_FLEET = ['named3', 'named2', 'named1', 'named4', 'named5', 'named6', 'named7', 'named8']

IGNORE_USERNAMES = ['muneeb', 'leena', 'chord', 'onename', 'blockstack', 'jp', 'to',
                    'usv', 'ycombinator', 'svangel', 'highline', 'openchain', 'contact', 'webmaster', 'user', 'ghandi']

DHT_IGNORE = ['thetodfather.id', 'hsingh.id', 'lauritzt.id']