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
    # 数据库连接编码
    'DB_CHARSET': 'utf8mb4',
    # mincached : 启动时开启的闲置连接数量(缺省值 0 开始时不创建连接)
    'DB_MIN_CACHED': 10,
    # maxcached : 连接池中允许的闲置的最多连接数量(缺省值 0 代表不闲置连接池大小)
    'DB_MAX_CACHED': 10,
    # maxshared : 共享连接数允许的最大数量(缺省值 0 代表所有连接都是专用的)
    # 如果达到了最大数量,被请求为共享的连接将会被共享使用
    'DB_MAX_SHARED': 20,
    # maxconnecyions : 创建连接池的最大数量(缺省值 0 代表不限制)
    'DB_MAX_CONNECYIONS': 100,
    # blocking : 设置在连接池达到最大数量时的行为(缺省值 0 或 False
    # 代表返回一个错误<toMany......> 其他代表阻塞直到连接数减少,连接被分配)
    'DB_BLOCKING': True,
    # maxusage : 单个连接的最大允许复用次数(缺省值 0 或 False 代表不限制的复用).
    # 当达到最大数时,连接会自动重新连接(关闭和重新打开)
    'DB_MAX_USAGE': 0,
    # setsession : 一个可选的SQL命令列表用于准备每个会话，
    # 如["set datestyle to german", ...]
    'DB_SET_SESSION': None
}

REDIS_SETTING = {
    "HOST": "146.56.219.98",
    "PORT": "16379",
    "PASSWORD": "Qm1lrYiMe8wx2sT7",
    "MAX_CONNECTIONS": 100
}

SINA_CLIENT_SECRET = "3372ad3b4b9750fc396546f52ccf68a1"
SINA_CLIENT_ID = "2310257607"
SINA_REDIRECT_URI = "http://146.56.219.98:8089/"
