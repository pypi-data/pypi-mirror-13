#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Registrar
    ~~~~~

    copyright: (c) 2014-2015 by Halfmoon Labs, Inc.
    copyright: (c) 2016 by Blockstack.org

This file is part of Registrar.

    Registrar is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Registrar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Registrar. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
from pymongo import MongoClient

# hack around absolute paths
current_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.abspath(current_dir + "/../../")

sys.path.insert(0, parent_dir)

from registrar.config import DEFAULT_NAMESPACE, RATE_LIMIT
from registrar.config import MINIMUM_LENGTH_NAME
from registrar.config import IGNORE_NAMES_STARTING_WITH
from registrar.config import SECRET_KEY

from registrar.utils import get_hash, check_banned_email, nmc_to_btc_address
from registrar.utils import config_log, ignoreRegistration
from registrar.utils import pretty_print as pprint

from registrar.states import registrationComplete, nameRegistered
from registrar.states import profilePublished
from registrar.server import RegistrarServer

from registrar.network import refresh_resolver

from registrar.crypto.bip38 import bip38_decrypt

"""
    Webapp Driver file that has all necessary functions for
    using registrar with webapp data
"""

log = config_log(__name__)

try:
    # incoming requests from a web app
    WEBAPP_DB_URI = os.environ['WEBAPP_DB_URI']
    WALLET_SECRET = os.environ['WALLET_SECRET']
except:
    log.debug("webapp_driver env variables not defined")
    exit(0)

webapp_db = MongoClient(WEBAPP_DB_URI).get_default_database()


def get_db_user_from_id(entry, users):
    """ Helper function for DB
    """

    user_id = entry['user_id']
    user = users.find_one({"_id": user_id})

    if user is None:
        return None

    if not user['username_activated']:
        return None

    return user


class WebappDriver(object):
    """ Registrar driver for webapp
    """

    def __init__(self):

        self.users = webapp_db.user
        self.registrations = webapp_db.user_registration
        self.updates = webapp_db.profile_update
        self.registrar_server = RegistrarServer()

    def process_new_users(self, nameop=None, spam_protection=False):
        """
            Process new registrations coming in on the webapp
        """

        counter = 0
        self.registrar_server.reset_flag()

        for new_user in self.registrations.find(no_cursor_timeout=True):

            user = get_db_user_from_id(new_user, self.users)

            if user is None:
                log.debug("No such user, need to remove: %s" % new_user['_id'])
                self.registrations.remove({'_id': new_user['_id']})
                continue

            # for spam protection
            if check_banned_email(user['email']):

                if spam_protection:
                    log.debug("Deleting spam %s, %s" % (user['email'], user['username']))
                    self.users.remove({"email": user['email']})
                else:
                    log.debug("Need to delete %s, %s" % (user['email'], user['username']))
                continue

            # test for minimum name length
            if len(user['username']) < MINIMUM_LENGTH_NAME:
                log.debug("Expensive name %s. Skipping." % user['username'])
                continue

            # test for ignoring names starting with certain patterns
            if ignoreRegistration(user['username'], IGNORE_NAMES_STARTING_WITH):
                log.debug("Ignoring: %s" % user['username'])
                continue

            fqu = user['username'] + "." + DEFAULT_NAMESPACE
            transfer_address = nmc_to_btc_address(user['namecoin_address'])
            profile = user['profile']

            log.debug("Processing: %s" % fqu)

            if registrationComplete(fqu, profile, transfer_address):
                log.debug("Registration complete %s. Removing." % fqu)
                self.registrations.remove({"user_id": new_user['user_id']})

                refresh_resolver(user['username'])
            else:
                try:
                    self.registrar_server.process_nameop(fqu, profile,
                                                         transfer_address,
                                                         nameop=nameop)
                except Exception as e:
                    log.debug(e)

    def update_users(self, spam_protection=False):
        """
            Process new profile updates from the webapp
        """

        counter = 0
        self.registrar_server.reset_flag()

        for new_user in self.updates.find(no_cursor_timeout=True):

            user = get_db_user_from_id(new_user, self.users)

            if user is None:
                continue

            # for spam protection
            if check_banned_email(user['email']):
                if spam_protection:
                    log.debug("Deleting spam: %s, %s" % (user['email'], user['username']))
                    self.updates.remove({"user_id": new_user['user_id']})
                else:
                    log.debug("Need to delete %s, %s" % (user['email'], user['username']))
                continue

            fqu = user['username'] + "." + DEFAULT_NAMESPACE
            btc_address = nmc_to_btc_address(user['namecoin_address'])
            profile = user['profile']
            encrypted_privkey = new_user['encrypted_private_key']
            hex_privkey = bip38_decrypt(str(encrypted_privkey), WALLET_SECRET)

            if nameRegistered(fqu):

                if profilePublished(fqu, profile):
                    log.debug("Profile match, removing: %s" % fqu)
                    self.updates.remove({"user_id": new_user['user_id']})

                    refresh_resolver(user['username'])
                else:
                    log.debug("Processing: %s, %s" % (fqu, user['email']))
                    try:
                        self.registrar_server.subsidized_nameop(fqu, profile,
                                                                hex_privkey=hex_privkey,
                                                                nameop='update')
                    except Exception as e:
                        log.debug(e)
            else:

                log.debug("Not registered: %s" % fqu)

    def reprocess_user(self, username):

        user = self.users.find_one({"username": username})
        fqu = user['username'] + "." + DEFAULT_NAMESPACE
        btc_address = nmc_to_btc_address(user['namecoin_address'])
        profile = user['profile']

        pprint(user)

        encrypted_privkey = user['encrypted_secret']
        hex_privkey = bip38_decrypt(str(encrypted_privkey), WALLET_SECRET)
        print hex_privkey
        log.debug("Reprocessing update: %s" % fqu)
        #update(fqu, profile, btc_address)

    def display_stats(self):

        log.debug("Pending registrations: %s" % self.registrations.find().count())
        log.debug("Pending updates: %s" % self.updates.find().count())
