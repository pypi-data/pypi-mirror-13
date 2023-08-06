from __future__ import absolute_import, division, print_function

from .processors import Match
from .processors import MatchError
from .processors import MethodProcessor
from .processors import PathProcessor
import operator

PROCESSORS = [
    PathProcessor('path'),
    MethodProcessor('method', optional=True),
]


class Avenue(object):
    def __init__(self, processors=None):
        self.routes = list()
        self.processors = processors or PROCESSORS

    def attach(self, **kwargs):
        def inner(func):
            self.routes.append(Route(self, kwargs, func))
            return func

        return inner

    def match(self, **kwargs):
        matches = list()

        for route in self.routes:
            try:
                match = Match()

                for processor in self.processors:
                    value = kwargs.get(processor.name)
                    match.update(processor(value, route))
            except MatchError:
                pass
            else:
                if len(match.score):
                    matches.append([route, match])

        size = max(map(len, [m[1].score for m in matches]))
        matches = list(filter(lambda m: len(m[1].score) == size, matches))
        matches.sort(key=operator.itemgetter(1))

        if len(matches):
            return matches[0][0], matches[0][1]
        else:
            return None, None


class Route(object):
    def __init__(self, avenue, kwargs, func):
        self.avenue = avenue
        self.kwargs = kwargs
        self.func = func
