# duckduckgo.py - Library for querying the DuckDuckGo API
#
# Copyright (c) 2010 Michael Stephens <me@mikej.st>
# Copyright (c) 2012-2013 Michael Smith <crazedpsyc@gshellz.org>
# Copyright (c) 2017 Members of the Programming Server
#
# See LICENSE for terms of usage, modification and redistribution.

import asyncio
import time

class _Scope:
    __slots__ = (
        'parent',
        'id',
    )

    def __init__(self, parent, id):
        self.parent = parent
        self.id = id

    def __enter__(self):
        duration = self.parent.left_to_wait(self.id)
        if duration > 0:
            time.sleep(duration)

    def __exit__(self, *exc):
        self.parent.update(self.id)

    async def __aenter__(self):
        duration = self.parent.left_to_wait(self.id)
        await asyncio.sleep(duration)

    async def __aexit__(self, *exc):
        self.__exit__(*exc)

class _TryScope:
    __slots__ = (
        'parent',
        'id',
        'ok',
    )

    def __init__(self, parent, id):
        self.parent = parent
        self.id = id
        self.ok = None

    def __enter__(self):
        duration = self.parent.left_to_wait(self.id)
        self.ok = (duration <= 0)
        return self.ok

    def __exit__(self, *exc):
        if self.ok:
            self.parent.update(self.id)

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, *exc):
        return self.__exit__(*exc)

class Ratelimit:
    __slots__ = (
        'frequency',
        'last_called',
    )

    def __init__(self, period=1, every=1.0):
        self.frequency = abs(every) / float(period)
        self.last_called = {}

    def left_to_wait(self, id=None):
        last = self.last_called.get(id, 0.0)
        elapsed = time.monotonic() - last
        return self.frequency - elapsed

    def check(self, id=None):
        return self.left_to_wait(id) <= 0

    def update(self, id=None):
        self.last_called[id] = time.monotonic()

    def run(self, id=None):
        return _Scope(self, id)

    def try_run(self, id=None):
        return _TryScope(self, id)
