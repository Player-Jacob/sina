#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/21 14:11
    author: Ghost
    desc: 
"""
from tornado.web import Application

from .api.sina import *
from config import setting
from libs import router


class App(Application):

    def __init__(self):
        print(router.Router.get_routes())
        super(App, self).__init__(
            handlers=router.Router.get_routes(),
            **setting.config.SETTINGS
        )


def create_app():
    return App()
