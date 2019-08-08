# duckduckgo.py - Library for querying the DuckDuckGo API
#
# Copyright (c) 2010 Michael Stephens <me@mikej.st>
# Copyright (c) 2012-2013 Michael Smith <crazedpsyc@gshellz.org>
# Copyright (c) 2017 Members of the Programming Server
#
# See LICENSE for terms of usage, modification and redistribution.

from ._version import __version__
from .query import DuckDuckGoError, query, zci
from .ratelimit import Ratelimit

__all__ = [
    'DuckDuckGoError',
    'query',
    'zci',
    'Ratelimit',
    '__version__',
]
