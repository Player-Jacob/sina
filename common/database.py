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

from config import setting


class ConnectionPool:
    __pool = None

    def __init__(self):
        self.conn = self._get_conn()
        self.cursor = self.conn.cursor()

    def _get_conn(self):
        if self.__pool is None:
            self.__pool = PooledDB(
                creator=pymysql,
                mincached=setting.MYSQL_SETTING['DB_MIN_CACHED'],
                maxcached=setting.MYSQL_SETTING['DB_MAX_CACHED'],
                maxshared=setting.MYSQL_SETTING['DB_MAX_SHARED'],
                maxconnections=setting.MYSQL_SETTING['DB_MAX_CONNECYIONS'],
                blocking=setting.MYSQL_SETTING['DB_BLOCKING'],
                maxusage=setting.MYSQL_SETTING['DB_MAX_USAGE'],
                setsession=setting.MYSQL_SETTING['DB_SET_SESSION'],
                host=setting.MYSQL_SETTING['HOST'],
                port=setting.MYSQL_SETTING['PORT'],
                user=setting.MYSQL_SETTING['USER'],
                passwd=setting.MYSQL_SETTING['PASSWORD'],
                db=setting.MYSQL_SETTING['NAME'],
                use_unicode=False,
                charset=setting.MYSQL_SETTING['DB_CHARSET']
            )
        return self.__pool.connection()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()

    def get_conn(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        return cursor, conn


def get_conn():
    return ConnectionPool()


def redis_cache():
    connection_pool = redis.ConnectionPool(
        host=setting.REDIS_SETTING['HOST'],
        port=setting.REDIS_SETTING['PORT'],
        password=setting.REDIS_SETTING['PASSWORD'],
        max_connections=setting.REDIS_SETTING['MAX_CONNECTIONS'],
    )
    return redis.Redis(connection_pool=connection_pool)
