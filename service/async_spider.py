#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/21 19:31
    author: Ghost
    desc: 
"""
import asyncio
import http.cookiejar
import logging
import os
import traceback
from http import cookiejar
from urllib.parse import urlencode

import aiohttp
from lxml import etree

from config import setting

class AsyncSpider:
    def __init__(self, url_list: list, max_threads: int):
        self.url_list = url_list
        self.results = {}
        self.max_threads = max_threads

    def __parse_results(self, url, html):
        selector = etree.HTML(html)
        print(html.decode('gbk'))

    @staticmethod
    async def download(url):
        cookie_path = os.path.join(setting.COOKIE_DIR, 'sina-cookies.txt')
        async_cookies = http.cookiejar.LWPCookieJar(cookie_path)
        async_cookies.load(ignore_discard=True)
        cookies_map = [(c.name, c.value) for c in async_cookies]
        cookies = aiohttp.cookiejar.CookieJar()
        cookies.update_cookies(cookies=cookies_map)
        async with aiohttp.ClientSession(cookies=cookies, connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.get(url, timeout=10) as response:
                print(response.request_info, 2222)
                html = await response.read()
                return response.url, html

    async def get_results(self, url):
        url, html = await self.download(url)
        self.__parse_results(url, html)

    async def handle_tasks(self, task_id, work_queue):
        while not work_queue.empty():
            current_url = await work_queue.get()
            try:
                await self.get_results(current_url)
            except Exception:
                logging.exception(f"url: {current_url} 解析失败：{traceback.format_exc()}")

    def event_loop(self):
        q = asyncio.Queue()
        for url in self.url_list:
            q.put_nowait(url)

        loop = asyncio.get_event_loop()
        tasks = [self.handle_tasks(task_id, q)for task_id in range(self.max_threads)]

        loop.run_until_complete(asyncio.wait(tasks))

        loop.close()


if __name__ == '__main__':
    params = {
        'q': '疫情',
        'typeall': '1',
        'suball': '1',
        'timescope': 'custom:2021-10-01:2021-10-03',
        'Refer': 'g'
    }
    url_list = []
    url = "https://s.weibo.com/weibo"
    for i in range(1, 2):
        params['page'] = i
        url_list.append(f"{url}/{urlencode(params)}")
    async_example = AsyncSpider(url_list, 5)
    async_example.event_loop()





