# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

from datetime import datetime, timedelta

from requests import post


class Token():

    def __init__(self):
        self.time = datetime.min
        self.key = 'invalid'

    def __str__(self):
        return self.key


class TranslateToken(Token):
    def update(self, config):
        client_id, secret = config['api']['translateid'], config['api']['translatesecret']
        # Don't die if we didn't setup the translate api.
        if not client_id:
            self.key = 'invalid'
            return
        postdata = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': secret, 'scope': 'http://api.microsofttranslator.com'}
        data = post('https://datamarket.accesscontrol.windows.net/v2/OAuth2-13', data=postdata).json()
        self.key = data['access_token']
        self.time = datetime.now()

token_cache = {'translate': TranslateToken()}


def update_all_tokens(config):
    for token in token_cache.values():
        # The cache is valid for 10 minutes, refresh it only if it will expire in 1 minute or less.
        if datetime.now() - token.time > timedelta(minutes=9):
            token.update(config)
