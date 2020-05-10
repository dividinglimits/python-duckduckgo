# duckduckgo.py - Library for querying the DuckDuckGo API
#
# Copyright (c) 2010 Michael Stephens <me@mikej.st>
# Copyright (c) 2012-2013 Michael Smith <crazedpsyc@gshellz.org>
# Copyright (c) 2017 Members of the Programming Server
#
# See LICENSE for terms of usage, modification and redistribution.

RESULT_TYPES = {
    "A": "answer",
    "D": "disambiguation",
    "C": "category",
    "N": "name",
    "E": "exclusive",
    "": "nothing",
}


class Results:
    __slots__ = (
        "type",
        "json",
        "api_version",
        "heading",
        "results",
        "related",
        "abstract",
        "redirect",
        "definition",
        "answer",
        "image",
    )

    def __init__(self, data):
        json_type = data.get("Type", "")
        self.type = RESULT_TYPES.get(json_type, "")

        self.json = data
        self.api_version = None  # compat

        self.heading = data.get("Heading", "")

        self.results = [Result(elem) for elem in data.get("Results", ())]
        self.related = [Result(elem) for elem in data.get("RelatedTopics", ())]

        self.abstract = Abstract(data)
        self.redirect = Redirect(data)
        self.definition = Definition(data)
        self.answer = Answer(data)

        self.image = Image({"Result": data.get("Image", "")})


class Abstract:
    __slots__ = (
        "html",
        "text",
        "url",
        "source",
    )

    def __init__(self, data):
        self.html = data.get("Abstract", "")
        self.text = data.get("AbstractText", "")
        self.url = data.get("AbstractURL", "")
        self.source = data.get("AbstractSource")


class Redirect:
    __slots__ = ("url",)

    def __init__(self, data):
        self.url = data.get("Redirect", "")


class Result:
    __slots__ = (
        "topics",
        "html",
        "text",
        "url",
        "icon",
    )

    def __init__(self, data):
        self.topics = data.get("Topics", [])
        if self.topics:
            self.topics = [Result(t) for t in self.topics]
            return
        self.html = data.get("Result")
        self.text = data.get("Text")
        self.url = data.get("FirstURL")

        icon_json = data.get("Icon")
        if icon_json is not None:
            self.icon = Image(icon_json)
        else:
            self.icon = None


class Image:
    __slots__ = (
        "url",
        "height",
        "width",
    )

    def __init__(self, data):
        self.url = data.get("Result")
        self.height = data.get("Height", None)
        self.width = data.get("Width", None)


class Answer:
    __slots__ = (
        "text",
        "type",
    )

    def __init__(self, data):
        self.text = data.get("Answer")
        self.type = data.get("AnswerType", "")


class Definition:
    __slots__ = (
        "text",
        "url",
        "source",
    )

    def __init__(self, data):
        self.text = data.get("Definition", "")
        self.url = data.get("DefinitionURL")
        self.source = data.get("DefinitionSource")
