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

from keychain import PrivateKeychain

from pybitcoin import make_send_to_address_tx
from pybitcoin import BlockcypherClient

from crypto.utils import get_address_from_privkey

from .utils import pretty_print as pprint
from .utils import config_log
from .utils import btc_to_satoshis

from .config import RATE_LIMIT
from .config import BLOCKCYPHER_TOKEN
from .config import TARGET_BALANCE_PER_ADDRESS, TX_FEE
from .config import CHAINED_PAYMENT_AMOUNT, MINIMUM_BALANCE
from .config import DEFAULT_CHILD_ADDRESSES

from .blockchain import get_balance, dontuseAddress, underfundedAddress

#from blockcypher import simple_spend_tx
from blockcypher import pushtx

log = config_log(__name__)
blockcypher_client = BlockcypherClient(api_key=BLOCKCYPHER_TOKEN)


class HDWallet(object):

    """
        Initialize a hierarchical deterministic wallet with
        hex_privkey and get child addresses and private keys
    """

    def __init__(self, hex_privkey=None):

        """
            If @hex_privkey is given, use that to derive keychain
            otherwise, use a new random seed
        """

        if hex_privkey:
            self.priv_keychain = PrivateKeychain.from_private_key(hex_privkey)
        else:
            self.priv_keychain = PrivateKeychain()

    def get_privkey(self, index=None):
        """
            @index is the child index

            Returns:
            master/root privkey by default
            or child privkey for given @index
        """

        if index is None:
            return self.priv_keychain.private_key()

        child = self.priv_keychain.hardened_child(index)
        return child.private_key()

    def get_address(self, index=None):
        """
            @index is the child index

            Returns:
            master/root address by default
            or child address for given @index
        """

        if index is None:
            hex_privkey = self.get_privkey()
            return get_address_from_privkey(hex_privkey)

        hex_privkey = self.get_privkey(index)
        return get_address_from_privkey(hex_privkey)

    def get_keypairs(self, count=None, include_privkey=False):
        """
            Returns (privkey, address) keypairs

            Returns:
            master/root pair by default
            if count is given, then returns child keypairs

            @include_privkey: toggles between option to return
                             privkeys along with addresses or not
        """

        keypairs = []

        if count is None:

            if include_privkey:
                keypairs.append((self.get_address(), self.get_privkey()))
            else:
                keypairs.append(self.get_address())

            return keypairs

        for index in range(count):
            hex_privkey = self.get_privkey(index)
            address = self.get_address(index)

            if include_privkey:
                keypairs.append((address, hex_privkey))
            else:
                keypairs.append(address)

        return keypairs

    def get_next_keypair(self, count=DEFAULT_CHILD_ADDRESSES):
        """ Get next payment address that is ready to use

            Returns (payment_address, hex_privkey)
        """

        addresses = self.get_keypairs(count=count)
        index = 0

        for payment_address in addresses:

            # find an address that can be used for payment

            if dontuseAddress(payment_address):
                log.debug("Pending tx on address: %s" % payment_address)

            elif underfundedAddress(payment_address):
                log.debug("Underfunded address: %s" % payment_address)

            else:
                return payment_address, self.get_privkey(index)

            index += 1

        log.debug("No valid address available.")

        return None, None


def get_underfunded_addresses(list_of_addresses):
    """
        Given a list of addresses, return the underfunded ones
    """

    underfunded_addresses = []

    for address in list_of_addresses:

        balance = get_balance(address)

        if balance <= float(MINIMUM_BALANCE):
            log.debug("address %s needs refill: %s"
                      % (address, balance))

            if dontuseAddress(address):
                log.debug("address %s has pending tx" % address)
            else:
                underfunded_addresses.append(address)

    return underfunded_addresses


def send_payment(hex_privkey, to_address, btc_amount):

    to_satoshis = btc_to_satoshis(btc_amount)
    fee_satoshis = btc_to_satoshis(TX_FEE)

    signed_tx = make_send_to_address_tx(to_address, to_satoshis, hex_privkey,
                                        blockchain_client=blockcypher_client,
                                        fee=fee_satoshis)

    resp = pushtx(tx_hex=signed_tx)

    if 'tx' in resp:
        return resp['tx']['hash']
    else:
        log.debug("ERROR: broadcasting tx")
        return resp


def display_wallet_info(list_of_addresses):

    for address in list_of_addresses:
        has_pending_tx = dontuseAddress(address)
        log.debug("(%s, balance %s,\t pending %s)" % (address,
                                                      get_balance(address),
                                                      has_pending_tx))

    log.debug("Total addresses: %s" % len(list_of_addresses))


if __name__ == '__main__':

    HEX_PRIV_KEY = os.environ['HEX_PRIV_KEY']
    wallet = HDWallet(HEX_PRIV_KEY)

    addresses = wallet.get_keypairs(5, include_privkey=False)
    print get_underfunded_addresses(addresses)
    print display_wallet_info(addresses)
    print wallet.get_next_keypair()
