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
import functools
import re
import time
import hashlib
import hmac
from io import BytesIO, StringIO
import csv

import requests
import jwt
from tornado.web import HTTPError

from config import setting
from common import async_decorator
from modules.sina import UserModel


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
    status_code = session.get(
        setting.SINA_LOGIN_URL.format(int(time.time() * 1000)),
        verify=False
    ).json()['code']
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


@async_decorator.decorator
def refresh_cookies(session, qr_id):
    headers = setting.HEADERS
    count = 0
    while 1 and count < 20:
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


def encrypt_hamc_sha256(secret: str, data: str):
    return hmac.new(secret.encode(), data.encode(),
                    digestmod=hashlib.sha256).hexdigest()


def create_token(user_id, username, exp):
    secret = setting.SECRET_KEY
    data = {
        "iss": "sina",
        "exp": exp,
        "aud": "sina",
        "user_id": user_id,
        "username": username
    }
    token = jwt.encode(data, secret, algorithm='HS256')
    data['grant_type'] = 'refresh'
    refresh_token = jwt.encode(data, secret, algorithm='HS256')
    return token, refresh_token


def decrypt_token(token):
    try:
        data = jwt.decode(token, setting.SECRET_KEY,
                          audience='sina', algorithms=['HS256'])
    except Exception:
        logging.warning(f'token decrypt failed:{traceback.format_exc()}')
        data = {}
    return data


def verify_refresh_token(token):
    payload = decrypt_token(token)
    # 校验token 是否有效，以及是否是refresh token，验证通过后生成新的token 以及 refresh_token
    if payload and payload.get('grant_type') == 'refresh':
        # 如果需要标记此token 已经使用，需要借助redis 或者数据库（推荐redis）
        return True, payload
    return False, None


def verify_bearer_token(token):
    #  如果在生成token的时候使用了aud参数，那么校验的时候也需要添加此参数
    payload = decrypt_token(token)
    # 校验token 是否有效，以及不能是refresh token
    if payload and payload.get('grant_type') != 'refresh':
        return True, payload
    return False, None


def login_check(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if 'Authorization' in self.request.headers:
            token = self.request.headers.get('Authorization').split()[-1]
        elif self.get_argument('token', ''):
            token = self.get_argument('token', '')
        else:
            raise HTTPError(401, '未登录')
        status, data = verify_bearer_token(token)
        user_id = data.get('user_id')
        username = data.get('username')
        cursor, conn = self.application.db_pool.get_conn()
        user = UserModel.get_user_by_id(user_id, cursor)
        if status and user and user['username'] == username:
            return method(self, *args, **kwargs)
        else:
            raise HTTPError(401, '登录失效')

    return wrapper


def refresh_token(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if 'Authorization' in self.request.headers:
            token = self.request.headers.get('Authorization').split()[-1]
        else:
            raise HTTPError(401, '未登录')
        status, data = verify_refresh_token(token)
        user_id = data.get('user_id')
        username = data.get('username')
        cursor, conn = self.application.db_pool.get_conn()
        user = UserModel.get_user_by_id(user_id, cursor)
        if status and user and user[1].decode() == username:
            return method(self, *args, **kwargs)
        else:
            raise HTTPError(401, '登录失效')

    return wrapper


def export_to_csv(self, filename, data):
        """接口返回文件

        Arguments:
            filename {str} -- 下载时显示的文件名
            data {list} -- 文件正文内容
            header {list} -- csv文件首行字说明
        """
        # http头 浏览器自动识别为文件下载
        self.set_header('Content-Type', 'application/octet-stream')
        # 下载时显示的文件名称
        self.set_header('Content-Disposition',
                        'attachment; filename={0}'.format(filename))
        csv_file = StringIO()
        csv_file.write('\ufeff')
        writer = csv.writer(csv_file, delimiter=',')
        for item in data:
            writer.writerow(item)
        self.write(csv_file.getvalue())
        return self.finish()


def get_sina_token(code):
    data = {
        'client_id': setting.SINA_CLIENT_ID,
        'client_secret': setting.SINA_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': setting.SINA_REDIRECT_URI
    }
    print(data, setting.SINA_AUTH_URL)
    try:
        resp = requests.post(setting.SINA_AUTH_URL, data=data).json()
    except Exception:
        logging.error(f'获取sina token 失败: \n 请求体：{data} \n {traceback.format_exc()}')
        return {}
    return resp


if __name__ == '__main__':
    session = get_session()
    is_login_sina(session)