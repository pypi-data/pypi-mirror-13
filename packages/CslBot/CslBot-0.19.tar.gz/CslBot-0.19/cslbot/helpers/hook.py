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

import functools
import re
import threading

from . import backtrace, modutils


class HookData(object):

    def __init__(self):
        self.known_hooks = {}
        self.disabled_hooks = set()

    def scan_for_hooks(self):
        """
        Scans for hooks

        :rtype: list
        :return: A list of modules that failed to reload
        """
        self.known_hooks.clear()
        self.disabled_hooks = modutils.get_disabled("hooks")
        errors = modutils.scan_and_reimport("hooks")
        return errors

    def get_known_hooks(self):
        return self.known_hooks

    def get_hook_objects(self):
        return [self.known_hooks[x] for x in self.known_hooks if x not in self.disabled_hooks]

    def get_enabled_hooks(self):
        return [x for x in self.known_hooks if x not in self.disabled_hooks]

    def get_disabled_hooks(self):
        return [x for x in self.known_hooks if x in self.disabled_hooks]

    def is_disabled(self, hook):
        return hook in self.disabled_hooks

    def disable_hook(self, hook):
        """Adds a hook to the disabled hooks list."""
        if hook not in self.known_hooks:
            return "%s is not a loaded hook" % hook
        if hook not in self.disabled_hooks:
            self.disabled_hooks.add(hook)
            return "Disabled hook %s" % hook
        else:
            return "That hook is already disabled!"

    def enable_hook(self, hook):
        """Removes a command from the disabled hooks list."""
        if hook == "all":
            self.disabled_hooks.clear()
            return "Enabled all hooks."
        elif hook in self.disabled_hooks:
            self.disabled_hooks.remove(hook)
            return "Enabled hook %s" % hook
        elif hook in self.known_hooks:
            return "That hook isn't disabled!"
        else:
            return "%s is not a loaded hook" % hook

    def register(self, hook):
        self.known_hooks[hook.name] = hook

registry = HookData()


class Hook():

    def __init__(self, name, types, args=[]):
        self.name = name
        self.types = [types] if isinstance(types, str) else types
        self.args = args
        registry.register(self)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(send, msg, msgtype, args):
            if msgtype in self.types:
                try:
                    thread = threading.current_thread()
                    thread_id = re.match(r'Thread-\d+', thread.name).group(0)
                    thread.name = "%s running %s" % (thread_id, func.__module__)
                    with self.handler.db.session_scope() as args['db']:
                        func(send, msg, args)
                except Exception as ex:
                    backtrace.handle_traceback(ex, self.handler.connection, self.target, self.handler.config, func.__module__)
                finally:
                    thread.name = "%s idle, last ran %s" % (thread_id, func.__module__)
        self.exe = wrapper
        return wrapper

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def run(self, send, msg, msgtype, handler, target, args):
        if registry.is_disabled(self.name):
            return
        self.handler = handler
        self.target = target
        handler.workers.start_thread(self.exe, send, msg, msgtype, args)
