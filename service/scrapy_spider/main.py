#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/25 18:42
    author: Ghost
    desc: 
"""
import os
import redis
import json


def start():
    conn = redis.Redis(host='146.56.219.98', port=16379, password='Qm1lrYiMe8wx2sT7')
    data = json.loads(conn.lrange('start_urls', 0, 10)[0])
    start_time = data['start_time']
    end_time = data['end_time']
    key_word = data['key']
    search_id = data['search_id']
    argv = ['scrapy', 'crawl', 'sina_spider', '-a', f'key_word={key_word}',
            '-a', f'start_time={start_time}', '-a', f'end_time={end_time}',
            '-a', f'search_id={search_id}']
    os.system(' '.join(argv))


if __name__ == '__main__':
    # key = '疫情'
    # start_time = '2021-10-15-10'
    # end_time = '2021-10-16-14'
    # search_id = 20
    start()

