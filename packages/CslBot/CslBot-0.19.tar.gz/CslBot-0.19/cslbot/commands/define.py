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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import random
import re

from lxml import etree

from requests import get

from ..helpers import arguments, textutils
from ..helpers.command import Command


def strip_colon(msg):
    return re.sub('^:|:$', '', msg.strip()).strip()


def get_def(entry, word, key):
    req = get('http://www.dictionaryapi.com/api/v1/references/collegiate/xml/%s' % word, params={'key': key})
    xml = etree.fromstring(req.content, parser=etree.XMLParser(recover=True))
    defs = []
    for defn in xml.findall('./entry/def/dt'):
        children = []
        for elem in defn.xpath('*[not(self::ca|self::dx|self::dx_def|self::vi|self::un|self::sx)]'):
            if elem.text is not None:
                children.append(strip_colon(elem.text))
            if elem.tail is not None:
                children.append(strip_colon(elem.tail))
        if defn.text is None:
            def_str = [' '.join(children)]
        else:
            def_str = []
            for x in strip_colon(defn.text).split(' :'):
                def_str.append(' '.join([x] + children))
        for x in filter(None, def_str):
            defs.append(x)
    if entry is None:
        entry = random.randrange(len(defs)) if defs else 0
    if entry >= len(defs):
        suggestion = xml.find('./suggestion')
        if suggestion is None:
            return None, None
        defn, _ = get_def(None, suggestion.text, key)
        if defn is None:
            return None, None
        else:
            return defn, suggestion.text
    else:
        return defs[entry], None


@Command('define', ['config'])
def cmd(send, msg, args):
    """Gets the definition of a word.
    Syntax: {command} [--entry <num>] <word>
    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('--entry', type=int, default=0, nargs='?')
    parser.add_argument('word', nargs='*')

    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    key = args['config']['api']['dictionaryapikey']
    if not cmdargs.word:
        for _ in range(5):
            word = textutils.gen_word()
            defn, suggested_word = get_def(None, word, key)
            word = suggested_word if suggested_word is not None else word
            if defn is not None:
                send("%s: %s" % (word, defn))
                return
        send("%s: Definition not found" % word)
        return
    word = ' '.join(cmdargs.word)
    defn, suggested_word = get_def(cmdargs.entry, word, key)
    if defn is None:
        send("Definition not found")
    elif suggested_word is None:
        send(defn)
    else:
        send("%s: %s" % (suggested_word, defn))
