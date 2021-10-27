#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/26 10:42
    author: Ghost
    desc: 
"""
import redis
import pymysql
from dbutils.pooled_db import PooledDB
from dbutils.persistent_db import PersistentDB

from config import setting


def redis_cache():
    connection_pool = redis.ConnectionPool(
        host=setting.REDIS_SETTING['HOST'],
        port=setting.REDIS_SETTING['PORT'],
        password=setting.REDIS_SETTING['PASSWORD'],
        max_connections=setting.REDIS_SETTING['MAX_CONNECTIONS'],
    )
    return redis.Redis(connection_pool=connection_pool)


def get_db_pool(is_mult_thread=True):
    db_config = {
        'host': setting.MYSQL_SETTING['HOST'],
        'port': setting.MYSQL_SETTING['PORT'],
        'database': setting.MYSQL_SETTING['NAME'],
        'user': setting.MYSQL_SETTING['USER'],
        'password': setting.MYSQL_SETTING['PASSWORD'],
        'charset': 'utf8'
    }
    print(db_config, 3333)
    if is_mult_thread:
        poolDB = PooledDB(
            # 指定数据库连接驱动
            creator=pymysql,
            # 连接池允许的最大连接数,0和None表示没有限制
            maxconnections=3,
            # 初始化时,连接池至少创建的空闲连接,0表示不创建
            mincached=2,
            # 连接池中空闲的最多连接数,0和None表示没有限制
            maxcached=5,
            # 连接池中最多共享的连接数量,0和None表示全部共享(其实没什么卵用)
            maxshared=3,
            # 连接池中如果没有可用共享连接后,是否阻塞等待,True表示等等,
            # False表示不等待然后报错
            blocking=True,
            # 开始会话前执行的命令列表
            setsession=[],
            # ping Mysql服务器检查服务是否可用
            ping=0,
            **db_config
        )
    else:
        poolDB = PersistentDB(
            # 指定数据库连接驱动
            creator=pymysql,
            # 一个连接最大复用次数,0或者None表示没有限制,默认为0
            maxusage=1000,
            **db_config
        )
    return poolDB