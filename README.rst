==================
python-duckduckgo
==================

A Python 3.6 library for querying the DuckDuckGo API.

Copyright (c) 2010 Michael Stephens <me@mikej.st>
Copyright (c) 2012-2013 Michael Smith <crazedpsyc@gshellz.org>
Copyright (c) 2017 Members of the Programming Server

Released under a 3-clause BSD license, see LICENSE for details.

This Source: https://github.com/strinking/python-duckduckgo
Original Source (1): http://github.com/crazedpsyc/python-duckduckgo
Original source (2): http://github.com/mikejs/python-duckduckgo

This version has been forked from the original to handle some new features of
the API, and switch from XML to JSON.

Installation
============

To install run

    ``python setup.py install``

Usage
=====

    >>> import duckduckgo
    >>> r = await duckduckgo.query('DuckDuckGo')
    >>> r.type
    'answer'
    >>> r.results[0].text
    'Official site'
    >>> r.results[0].url
    'http://duckduckgo.com/'
    >>> r.abstract.url
    'http://en.wikipedia.org/wiki/Duck_Duck_Go'
    >>> r.abstract.source
    'Wikipedia'

    >>> r = await duckduckgo.query('Python')
    >>> r.type
    u'disambiguation'
    >>> r.related[1].text
    u'Python (programming language), a computer programming language'
    >>> r.related[1].url
    u'http://duckduckgo.com/Python_(programming_language)'
    >>> r.related[7].topics[0].text # weird, but this is how the DDG API is currently organized
    u'Armstrong Siddeley Python, an early turboprop engine'


    >>> r = await duckduckgo.query('1 + 1')
    >>> r.type
    u'nothing'
    >>> r.answer.text
    u'1 + 1 = 2'
    >>> r.answer.type
    u'calc'

    >>> print(await duckduckgo.query('19301', kad='es_ES').answer.text)
    19301 es un código postal de Paoli, PA
    >>> print(await duckduckgo.query('how to spell test', html=True).answer.text)
    <b>Test</b> appears to be spelled right!<br/><i>Suggestions: </i>test, testy, teat, tests, rest, yest.

The easiest method of quickly grabbing the best (hopefully) API result is to use duckduckgo.zci::
    >>> print duckduckgo.zci('foo')
    The terms foobar /ˈfʊːbɑːr/, fubar, or foo, bar, baz and qux are sometimes used as placeholder names in computer programming or computer-related documentation. (https://en.wikipedia.org/wiki/Foobar)
    >>> print ddg.zci('foo fighters site')
    http://www.foofighters.com/us/home

Special keyword args for query():
 - useragent   - string, The useragent used to make API calls. This is somewhat irrelevant, as they are not logged or used on DuckDuckGo, but it is retained for backwards compatibility.
 - safesearch  - boolean, enable or disable safesearch.
 - html        - boolean, Allow HTML in responses?

