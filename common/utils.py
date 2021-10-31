#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/21 14:25
    author: Ghost
    desc: 
"""
import asyncio
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
    cookie_path = os.path.join(setting.COOKIE_DIR, 'sina-cookies.txt')

    if not os.path.exists(setting.COOKIE_DIR):
        os.mkdir(setting.COOKIE_DIR)
    if not os.path.exists(cookie_path):
        with open(cookie_path, 'w') as f:
            f.write("")

    session = requests.session()
    session.cookies = cookiejar.LWPCookieJar(filename=cookie_path)
    try:
        session.cookies.load(ignore_discard=True)
    except cookiejar.LoadError:
        pass
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'Referer': "https://weibo.com/"
    })
    return session


def is_login_sina(session):
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


def refresh_cookies(session, qr_id):
    headers = setting.HEADERS
    count = 0
    while 1 and count < 5:
        dateurl = session.get(setting.SINA_QR_ID_URL.format(qr_id, int(time.time() * 1000), headers=headers)).text
        xx = re.search("window.STK_\d+.\d+ && STK_\d+.\d+\(?", dateurl)
        x = json.loads(dateurl.strip().lstrip(xx.group()).rstrip(");"))
        retcode = x['retcode']
        if '50114001' in str(retcode):
            logging.info('二维码未失效，请扫码！')
        elif '50114002' in str(retcode):
            logging.info('已扫码，请确认！')
        elif '50114004' in str(retcode):
            logging.info('二维码已失效，请重新运行！')
        elif '20000000' in str(retcode):
            alt = x['data']['alt']
            alturl = 'https://login.sina.com.cn/sso/login.php?entry=weibo&returntype=TEXT&crossdomain=1&cdult=3&domain=weibo.com&alt={}&savestate=30&callback=STK_{}'.format(
                alt, int(time.time() * 100000))
            crossDomainUrl = session.get(alturl, headers=headers).text
            pp = re.search("STK_\d+\(?", crossDomainUrl)
            p = json.loads(crossDomainUrl.strip().lstrip(pp.group()).rstrip(");"))
            crossDomainUrlList = p['crossDomainUrlList']
            session.get(crossDomainUrlList[0], headers=headers)
            session.get(crossDomainUrlList[1] + '&action=login', headers=headers)
            session.get(crossDomainUrlList[2], headers=headers)
            # session.get(crossDomainUrlList[3], headers=headers)
            logging.info('已确认，登录成功！')
            break
        else:
            logging.info('其他情况', retcode)
        count += 1
        time.sleep(5)
    if count < 20:
        session.cookies.save()
        logging.info('cookies 刷新成功')
    else:
        logging.info('cookies 刷新失败')


if __name__ == '__main__':
    session = get_session()
    is_login_sina(session)