#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/21 14:44
    author: Ghost
    desc: 
"""
import logging
import os

DEPLOY = "online"
LOGGER_LEVEL = logging.INFO
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

THREAD_MAX_WORKERS = 100

SETTINGS = {
    "debug": False,
    "template_path": os.path.join(PROJECT_ROOT, "templates"),
    "static_path": os.path.join(PROJECT_ROOT, "static"),
    "xsrf_cookies": False,
}

MYSQL_SETTING = {
    "HOST": "",
    "NAME": "",
    "USER": "",
    "PASSWORD": "",
    "PORT": "",
}


REDIS_SETTING = {
    "HOST": "",
    "PORT": "",
    "PASSWORD": ""
}

SCRAPY_LOG_LEVEL = 'INFO'


KAFKA_REFRESH_SERVICE = {
    'TOPIC': 'refresh',
    'GROUP_ID': 'sina_refresh',
    'bootstrap_servers': ''  # 172.28.48.58:19093
}
