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
        'max_count',
        'duration',
        'limited',
    )

    def __init__(self, count=1, every=1.0):
        self.max_count = count
        self.duration = float(every)
        self.limited = {} # { id : (count, last_time) }

    def left_to_wait(self, id=None):
        count, last_time = self.limited.get(id, (0, 0.0))
        if count < self.max_count - 1:
            return 0.0

        elapsed = time.monotonic() - last_time
        return self.duration - elapsed

    def check(self, id=None):
        return self.left_to_wait(id) <= 0

    def update(self, id=None):
        count, last_time = self.limited.get(id, (0, 0.0))
        now = time.monotonic()
        elapsed = now - last_time
        if elapsed > self.duration:
            self.limited[id] = (0, now)
        else:
            self.limited[id] = (count + 1, last_time)

    def run(self, id=None):
        return _Scope(self, id)

    def try_run(self, id=None):
        return _TryScope(self, id)
