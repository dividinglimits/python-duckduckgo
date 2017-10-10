# duckduckgo.py - Library for querying the DuckDuckGo API
#
# Copyright (c) 2010 Michael Stephens <me@mikej.st>
# Copyright (c) 2012-2013 Michael Smith <crazedpsyc@gshellz.org>
# Copyright (c) 2017 Members of the Programming Server
#
# See LICENSE for terms of usage, modification and redistribution.

import urllib.parse
from typing import Tuple

import aiohttp
from ratelimit import rate_limited

from . import __version__
from .models import Results

DEFAULT_USER_AGENT = f'python-duckduckgo {__version__}'
DEFAULT_PRIORITIES = ('answer', 'abstract', 'related.0', 'definition')

@rate_limited(1)
async def query(q: str,
                useragent: str = DEFAULT_USER_AGENT,
                safesearch: bool = True,
                html: bool = False,
                meanings: bool = True,
                **kwargs) -> Results:
    """
    Query DuckDuckGo, returning a Results object.

    The API is queried asynchronously, and redirects are followed.

    Keyword arguments:
    useragent: UserAgent to use while querying. Default: "python-duckduckgo <version>" (str)
    safesearch: True for on, False for off. Default: True (bool)
    html: True to allow HTML in output. Default: False (bool)
    meanings: True to include disambiguations in results (bool)
    Any other keyword arguments are passed directly to DuckDuckGo as URL params.
    """

    safesearch = '1' if safesearch else '-1'
    html = '0' if html else '1'
    meanings = '0' if meanings else '1'
    params = {
        'q': q,
        'o': 'json',
        'kp': safesearch,
        'no_redirect': '1',
        'no_html': html,
        'd': meanings,
    }
    params.update(kwargs)
    encparams = urllib.parse.urlencode(params)
    url = f'http://api.duckduckgo.com/?{encparams}'

    async with aiohttp.ClientSession() as cs:
        async with cs.get(url, headers={'User-Agent': useragent}) as req:
            response = await req.json(content_type='application/x-javascript')
            if response is None:
                raise ValueError("Failed to decode JSON response")
    return Results(response)

async def get_zci(q: str,
        web_fallback: bool = True,
        priority: Tuple[str] = DEFAULT_PRIORITIES,
        urls: bool = True,
        **kwargs) -> str:
    '''A helper method to get a single (and hopefully the best) ZCI result.
    priority=list can be used to set the order in which fields will be checked for answers.
    Use web_fallback=True to fall back to grabbing the first web result.
    passed to query. This method will fall back to 'Sorry, no results.'
    if it cannot find anything.'''

    ddg = await query(f'\\{q}', **kwargs)
    response = ''

    for p in priority:
        ps = p.split('.')
        type = ps[0]
        index = int(ps[1]) if len(ps) > 1 else None

        result = getattr(ddg, type)
        if index is not None:
            if not hasattr(result, '__getitem__'):
                raise TypeError(f'{type} field is not indexable')
            result = result[index] if len(result) > index else None
        if not result:
            continue

        if result.text:
            response = result.text
        if result.text and hasattr(result, 'url') and urls:
            if result.url:
                response += f' ({result.url})'
        if response:
            break

    # If there still isn't anything, try to get the first web result
    if not response and web_fallback:
        if ddg.redirect.url:
            response = ddg.redirect.url

    # Final fallback
    if not response:
        response = 'Sorry, no results.'

    return response
