#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/21 14:34
    author: Ghost
    desc: 
"""
import logging
import os.path
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
SINA_ACCOUNT_URL = "https://account.weibo.com/set/aj/iframe/schoollist?province=11&city=&type=1&_t=0&__rnd={}"
SINA_QR_ID_URL = 'https://login.sina.com.cn/sso/qrcode/check?entry=weibo&qrid={}&callback=STK_{}'
COOKIE_DIR = config.SETTINGS['static_path']
COOKIE_PATH = os.path.join(config.SETTINGS['static_path'], 'sina-cookies.txt')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
    'Referer': "https://weibo.com/"
}

MYSQL_SETTING = config.MYSQL_SETTING

LOG_PATH = os.path.join(config.PROJECT_ROOT, 'logs')
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)

REDIS_SETTING = config.REDIS_SETTING

SPIDER_STATUS_KEY = 'spider_finished:{}'


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

