#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/22 10:11
    author: Ghost
    desc: 
"""
import aiohttp
import asyncio

async def fetch(session, url):
    async with session.get(url) as response:
        session.cookie_jar.save('test.txt')
        return await response.text()


async def main():
    async with aiohttp.ClientSession(cookies=aiohttp.CookieJar(), connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        html = await fetch(session, "https://www.baidu.com")
        # print(html)

asyncio.run(main())
