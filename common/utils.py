#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/21 14:25
    author: Ghost
    desc: 
"""
import logging
import json
import traceback
from http import cookiejar
import os
import os.path
import re
import time

import requests
from config import setting


def get_session():
    cookie_path = os.path.join(setting.COOKIE_PATH, 'sina-cookies.txt')

    if not os.path.exists(setting.COOKIE_PATH):
        os.mkdir(setting.COOKIE_PATH)
    if not os.path.exists(cookie_path):
        with open(cookie_path, 'w') as f:
            f.write("")

    session = requests.session()
    session.cookies = cookiejar.LWPCookieJar(filename=cookie_path)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'Referer': "https://weibo.com/"
    })
    return session


def is_login_sina(session):
    try:
        session.cookies.load(ignore_discard=True)
    except Exception:
        pass
    status_code = session.get(setting.SINA_LOGIN_URL.format(int(time.time() * 1000))).json()['code']
    if status_code == '100000':
        logging.info('Cookies值有效，无需扫码登录！')
        return True
    else:
        logging.info('Cookies值已经失效，请重新扫码登录！')
        return False


def get_qr_code(session):
    resp = session.get(setting.SINA_QRCODE_URL.format(int(time.time() * 1000))).text
    try:
        json_resp = json.loads(re.findall(r"\((\{.*?\})\)", resp)[0])
    except Exception:
        logging.warning('解析json失败：{}'.format(traceback.format_exc()))
        json_resp = {}

    data = json_resp.get('data', {})
    qr_id = data.get('qrid', '')
    image = data.get('image', '')
    return qr_id, "https://{}".format(image) if image else ""


if __name__ == '__main__':
    is_login_sina(get_session())
    get_qr_code(get_session())