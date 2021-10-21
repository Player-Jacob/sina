#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/21 14:17
    author: Ghost
    desc: 
"""
import tornado.web


class Router:

    routes = []

    def __init__(self, uri, name=None):
        self._uri = uri
        self.name = name

    def __call__(self, _handler, *args, **kwargs):
        name = self.name and self.name or _handler.__name__
        self.routes.append(tornado.web.url(self._uri, _handler, name=name))
        return _handler

    @classmethod
    def get_routes(cls):
        return cls.routes


def route_redirect(_from, to, name=None):
    Router.routes.append(tornado.web.url(
        _from, tornado.web.RedirectHandler, dict(url=to), name=name))
