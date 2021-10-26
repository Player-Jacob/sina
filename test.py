#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/22 10:11
    author: Ghost
    desc: 
"""
import aiohttp
import asyncio
#
# async def fetch(session, url):
#     async with session.get(url) as response:
#         session.cookie_jar.save('test.txt')
#         return await response.text()
#
#
# async def main():
#     async with aiohttp.ClientSession(cookies=aiohttp.CookieJar(), connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
#         html = await fetch(session, "https://www.baidu.com")
#         # print(html)
#
# asyncio.run(main())
import pymysql
from dbutils.pooled_db import PooledDB
db_config = {'host': '146.56.219.98', 'port': 3506, 'database': 'sina', 'user': 'lichunxu', 'password': 'TT4RVhRjlJUwjEj*', 'charset': 'utf8'}
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
conn = poolDB.connection()
cursor = conn.cursor()
cursor.execute('show tables;')
cursor.execute('select * from sina_weibo limit 10')
result = cursor.fetchall()
print(dir(conn._con))
print(dir(cursor._cursor))
print(len(result))