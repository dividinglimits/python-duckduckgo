# duckduckgo.py - Library for querying the DuckDuckGo API
#
# Copyright (c) 2010 Michael Stephens <me@mikej.st>
# Copyright (c) 2012-2013 Michael Smith <crazedpsyc@gshellz.org>
# Copyright (c) 2017 Members of the Programming Server
#
# See LICENSE for terms of usage, modification and redistribution.

import os

__all__ = [
    '__version__',
]

path = os.path.join(os.path.dirname(__file__), 'VERSION')
with open(path) as fh:
    __version__ = fh.read().strip()
