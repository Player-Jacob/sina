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
from common import database


class App(Application):

    def __init__(self):
        routers = router.Router.get_routes()
        super(App, self).__init__(
            handlers=routers,
            **setting.config.SETTINGS
        )
        self.redis_cache = database.redis_cache()
        self.db_pool = database.get_conn()


def create_app():
    return App()
