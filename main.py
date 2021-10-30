#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/21 14:11
    author: Ghost
    desc: 
"""
import asyncio

from tornado import httpserver
from tornado import ioloop
# import uvloop

from app import create_app
from config import setting

if __name__ == '__main__':
    # asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logger = setting.get_logger()
    app = create_app()
    server = httpserver.HTTPServer(app, xheaders=True)
    server.listen(setting.port)
    logger.info(f'start listening on port :{setting.port}')
    ioloop.IOLoop.current().start()

