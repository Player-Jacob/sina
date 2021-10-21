#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/21 14:34
    author: Ghost
    desc: 
"""
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from tornado.util import import_object
from tornado.options import define, options

define('env', default='test')
define('port', default=8000)
options.parse_command_line()

port = options.port
config = import_object("config.{env}".format(env=options.env))


# ThreadPoolExecutor for IO intensive, ProcessPoolExecutor for CPU intensive
thread_executor = ThreadPoolExecutor(config.THREAD_MAX_WORKERS)
process_executor = ProcessPoolExecutor()

SINA_LOGIN_URL = "https://account.weibo.com/set/aj/iframe/schoollist?province=11&city=&type=1&_t=0&__rnd={}"
SINA_QRCODE_URL = "https://login.sina.com.cn/sso/qrcode/image?entry=weibo&size=180&callback=STK_{}"
COOKIE_PATH = config.SETTINGS['static_path']


def get_logger():
    logger = logging.getLogger()
    formatter = logging.Formatter(
        "[%(levelname)s %(asctime)s] [%(filename)s %(lineno)d %(funcName)s %(process)d %(threadName)s] %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.setLevel(config.LOGGER_LEVEL)
    logger.handlers = []
    logger.addHandler(sh)
    return logger

