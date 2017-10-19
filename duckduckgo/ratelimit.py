# duckduckgo.py - Library for querying the DuckDuckGo API
#
# Copyright (c) 2010 Michael Stephens <me@mikej.st>
# Copyright (c) 2012-2013 Michael Smith <crazedpsyc@gshellz.org>
# Copyright (c) 2017 Members of the Programming Server
#
# See LICENSE for terms of usage, modification and redistribution.

import asyncio
import time

class Ratelimit:
    __slots__ = (
        'frequency',
        'last_called',
    )

    def __init__(self, period=1, every=1.0):
        self.frequency = abs(every) / float(period)
        self.last_called = {}

    def left_to_wait(self, id):
        last = self.last_called.get(id, 0.0)
        elapsed = time.monotonic() - last
        return self.frequency - elapsed

    def check(self, id):
        return self.left_to_wait(id) <= 0

    def update(self, id):
        self.last_called[id] = time.monotonic()

    def call(self, id, func, *args, **kwargs):
        duration = self.left_to_wait(id)
        if duration > 0:
            time.sleep(duration)

        return func(*args, **kwargs)

    async def async_call(self, id, coro, *args, **kwargs):
        duration = self.left_to_wait(id)
        if duration > 0:
            await asyncio.sleep(duration)

        return await coro(*args, **kwargs)

    def try_call(self, id, func, *args, **kwargs):
        if not self.check(id):
            return (False, None)

        self.update(id)
        return (True, func(*args, **kwargs))

    async def try_async_call(self, id, coro, *args, **kwargs):
        if not self.check(id):
            return (False, None)

        self.update(id)
        return (True, await coro(*args, **kwargs))
