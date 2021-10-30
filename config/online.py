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
    "HOST": "localhost",
    "NAME": "sina",
    "USER": "sina",
    "PASSWORD": "mN7cJXZJcWtzEFz3",
    "PORT": "3306",
}

REDIS_SETTING = {
    "HOST": "localhost",
    "PORT": "6379",
    "PASSWORD": "",
    "MAX_CONNECTIONS": "100"
}
