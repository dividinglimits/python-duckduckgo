# duckduckgo.py - Library for querying the DuckDuckGo API
#
# Copyright (c) 2010 Michael Stephens <me@mikej.st>
# Copyright (c) 2012-2013 Michael Smith <crazedpsyc@gshellz.org>
#
# See LICENSE for terms of usage, modification and redistribution.

import urllib.parse

import aiohttp
from ratelimit import rate_limited

__version__ = 0.242


@rate_limited(1)
async def query(query, useragent='python-duckduckgo ' + str(__version__),
                safesearch=True, html=False, meanings=True, **kwargs):
    """
    Query DuckDuckGo, returning a Results object.

    The API is queried asynchronously, and redirects are followed.

    Keyword arguments:
    useragent: UserAgent to use while querying. Default: "python-duckduckgo %d" (str)
    safesearch: True for on, False for off. Default: True (bool)
    html: True to allow HTML in output. Default: False (bool)
    meanings: True to include disambiguations in results (bool)
    Any other keyword arguments are passed directly to DuckDuckGo as URL params.
    """ % __version__

    safesearch = '1' if safesearch else '-1'
    html = '0' if html else '1'
    meanings = '0' if meanings else '1'
    params = {
        'q': query,
        'o': 'json',
        'kp': safesearch,
        'no_redirect': '0',
        'no_html': html,
        'd': meanings,
    }
    params.update(kwargs)
    encparams = urllib.parse.urlencode(params)
    url = 'http://api.duckduckgo.com/?' + encparams
    async with aiohttp.ClientSession() as cs:
        async with cs.get('http://api.duckduckgo.com/?' + encparams,
                          headers={'User-Agent': useragent}) as r:
            print(r)
            print(await r.read())
            response_json = await r.json(content_type='application/x-javascript')

    if response_json is None:
        print(r)
        print(await r.read())
        raise ValueError("Failed to decode JSON response")
    return Results(response_json)


class Results(object):

    def __init__(self, data):
        json_type = data.get('Type', '')
        self.type = {'A': 'answer', 'D': 'disambiguation',
                     'C': 'category', 'N': 'name',
                     'E': 'exclusive', '': 'nothing'}.get(json_type, '')

        self.json = data
        self.api_version = None  # compat

        self.heading = data.get('Heading', '')

        self.results = [Result(elem) for elem in data.get('Results', [])]
        self.related = [Result(elem) for elem in
                        data.get('RelatedTopics', [])]

        self.abstract = Abstract(data)
        self.redirect = Redirect(data)
        self.definition = Definition(data)
        self.answer = Answer(data)

        self.image = Image({'Result': data.get('Image', '')})


class Abstract(object):

    def __init__(self, data):
        self.html = data.get('Abstract', '')
        self.text = data.get('AbstractText', '')
        self.url = data.get('AbstractURL', '')
        self.source = data.get('AbstractSource')


class Redirect(object):

    def __init__(self, data):
        self.url = data.get('Redirect', '')


class Result(object):

    def __init__(self, data):
        self.topics = data.get('Topics', [])
        if self.topics:
            self.topics = [Result(t) for t in self.topics]
            return
        self.html = data.get('Result')
        self.text = data.get('Text')
        self.url = data.get('FirstURL')

        icon_json = data.get('Icon')
        if icon_json is not None:
            self.icon = Image(icon_json)
        else:
            self.icon = None


class Image(object):

    def __init__(self, data):
        self.url = data.get('Result')
        self.height = data.get('Height', None)
        self.width = data.get('Width', None)


class Answer(object):

    def __init__(self, data):
        self.text = data.get('Answer')
        self.type = data.get('AnswerType', '')


class Definition(object):
    def __init__(self, data):
        self.text = data.get('Definition', '')
        self.url = data.get('DefinitionURL')
        self.source = data.get('DefinitionSource')


async def get_zci(q, web_fallback=True,
                  priority=['answer', 'abstract', 'related.0', 'definition'],
                  urls=True, **kwargs):
    '''A helper method to get a single (and hopefully the best) ZCI result.
    priority=list can be used to set the order in which fields will be checked for answers.
    Use web_fallback=True to fall back to grabbing the first web result.
    passed to query. This method will fall back to 'Sorry, no results.'
    if it cannot find anything.'''

    ddg = await query('\\' + q, **kwargs)
    response = ''

    for p in priority:
        ps = p.split('.')
        type = ps[0]
        index = int(ps[1]) if len(ps) > 1 else None

        result = getattr(ddg, type)
        if index is not None:
            if not hasattr(result, '__getitem__'):
                raise TypeError('%s field is not indexable' % type)
            result = result[index] if len(result) > index else None
        if not result:
            continue

        if result.text:
            response = result.text
        if result.text and hasattr(result, 'url') and urls:
            if result.url:
                response += ' (%s)' % result.url
        if response:
            break

    # if there still isn't anything, try to get the first web result
    if not response and web_fallback:
        if ddg.redirect.url:
            response = ddg.redirect.url

    # final fallback
    if not response:
        response = 'Sorry, no results.'

    return response
