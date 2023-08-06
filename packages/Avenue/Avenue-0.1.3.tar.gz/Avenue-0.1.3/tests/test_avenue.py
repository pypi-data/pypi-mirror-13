# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from avenue import Avenue


class TestAvenue(object):
    def test_basics(self):
        router = Avenue()

        @router.attach(path='/', method='GET')
        @router.attach(path='/welcome')
        def route_1():
            return 'Route 1'

        @router.attach(path='/', method='POST')
        def route_2():
            return 'Route 2'

        @router.attach(path='/post/<id|int>')
        def route_3(id):
            return 'Route 3 - for {:s}'.format(repr(id))

        @router.attach(path='/post/new')
        def route_4():
            return 'Route 4'

        @router.attach(path='/<page|greedy>')
        def route_5(page):
            return 'Route 5 - fallback - {:s}'.format(page)

        routing = [
            [{'path': '/', 'method': 'GET'},
             'Route 1'],
            [{'path': '/', 'method': 'POST'},
             'Route 2'],
            [{'path': '/post/12', 'method': 'GET'},
             'Route 3 - for 12'],
            [{'path': '/post/new-article-here', 'method': 'GET'},
             'Route 5 - fallback - post/new-article-here'],
            [{'path': '/post/new', 'method': 'GET'},
             'Route 4'],
            [{'path': '/any/other/page', 'method': 'GET'},
             'Route 5 - fallback - any/other/page'],
        ]

        for route, result in routing:
            path, match = router.match(**route)
            assert path.func(**match.kwargs) == result
