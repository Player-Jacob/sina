#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/21 14:43
    author: Ghost
    desc: 
"""
import logging
import os

DEPLOY = "test"
LOGGER_LEVEL = logging.DEBUG
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

THREAD_MAX_WORKERS = 100

SETTINGS = {
    "debug": True,
    "template_path": os.path.join(PROJECT_ROOT, "templates"),
    "static_path": os.path.join(PROJECT_ROOT, "static"),
    "xsrf_cookies": False,
}

MYSQL_SETTING = {
    "HOST": "146.56.219.98",
    "NAME": "sina",
    "USER": "lichunxu",
    "PASSWORD": "TT4RVhRjlJUwjEj*",
    "PORT": 3506,
}

SCRAPY_LOG_LEVEL = 'DEBUG'

REDIS_SETTING = {
    "HOST": "146.56.219.98",
    "PORT": "16379",
    "PASSWORD": "Qm1lrYiMe8wx2sT7",
    "MAX_CONNECTIONS": 100
}

KAFKA_REFRESH_SERVICE = {
    'TOPIC': 'refresh',
    'GROUP_ID': 'sina_refresh',
    'BOOTSTRAP_SERVERS': '146.56.219.98:9092'  # 172.28.48.58:19093
}
