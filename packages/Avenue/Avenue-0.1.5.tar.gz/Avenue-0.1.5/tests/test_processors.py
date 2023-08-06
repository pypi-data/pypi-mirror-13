# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from avenue import Avenue
from avenue.processors import Match
from avenue.processors import PathProcessor
from pytest import raises


class TestProcessors(object):
    def test_match(self):
        match = Match()
        match.update(2)
        match.update(1)

        assert repr(match) == '<Match (score=[2, 1])>'

    def test_path_processor(self):
        avenue = Avenue([
            PathProcessor('path_1'),
            PathProcessor('path_2', optional=True),
        ])

        @avenue.attach(path_1='/welcome', path_2='/nl')
        def nl_welcome():
            pass

        @avenue.attach(path_1='/welcome', path_2='/de-DE')
        def de_welcome():
            pass

        @avenue.attach(path_1='/welcome')
        def welcome():
            pass

        path, match = avenue.match(path_1='/welcome', path_2='/de-DE')
        assert path.func is de_welcome

        path, match = avenue.match(path_1='/welcome')
        assert path.func is welcome

    def test_exceptions(self):
        avenue = Avenue()

        @avenue.attach()
        def will_never_run():
            pass

        with raises(RuntimeError):
            avenue.match()
