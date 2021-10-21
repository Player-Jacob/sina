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
