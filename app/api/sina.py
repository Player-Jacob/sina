#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/21 15:43
    author: Ghost
    desc: 
"""
from subprocess import run
import json
import logging
import re
import time
import traceback
import datetime


from common import helper, utils
from libs import router
from config import setting
from modules.sina import SearchHistoryModel, ArticleListModel, CommentListModel,\
    UserModel, LabelRuleModel


@router.Router("/api/v1/qr-cord-url")
class ApiSinaIndexHandler(helper.ApiBaseHandler):
    @utils.login_check
    def get(self, *args, **kwargs):
        session = utils.get_session()
        status = utils.is_login_sina(session)
        if not status:
            qr_id, image = utils.get_qr_code(session)
            logging.info("qr_id: {}, image: {}".format(qr_id, image))
            data = dict(isLogin=status, image=image)
            self.jsonify_finish(is_succ=True, data=data)
            utils.refresh_cookies(session, qr_id)
        else:
            data = dict(isLogin=status)
            self.jsonify_finish(is_succ=True, data=data)


@router.Router("/api/v1/check-login")
class ApiSinaCheckHandler(helper.ApiBaseHandler):
    @utils.login_check
    def get(self, *args, **kwargs):
        session = utils.get_session()
        status = utils.is_login_sina(session)
        data = dict(isLogin=status)
        return self.jsonify_finish(is_succ=True, data=data)


@router.Router("/api/v1/check-spider")
class ApiSinaCheckHandler(helper.ApiBaseHandler):
    @utils.login_check
    def get(self, *args, **kwargs):
        search_id = self.get_argument('searchId', '')
        if not search_id:
            return self.jsonify_finish(error_msg='缺少参数')
        redis_key = setting.SPIDER_STATUS_KEY.format(search_id)
        status = True if self.redis_cache.get(redis_key) else False
        if status:
            self.redis_cache.delete(redis_key)
        data = dict(status=status)
        return self.jsonify_finish(is_succ=True, data=data)


@router.Router("/api/v1/sina-search")
class ApiSinaSearchHandler(helper.ApiBaseHandler):
    @utils.login_check
    def post(self, *args, **kwargs):
        try:
            resp_data = json.loads(self.request.body)
        except Exception:
            logging.error(f'参数异常 {traceback.format_exc()}')
            return self.jsonify_finish(error_msg='系统异常')
        keyword = resp_data.get('keyword')
        start_time = resp_data.get('startTime')
        end_time = resp_data.get('endTime')
        if not all([keyword, start_time, end_time]):
            return self.jsonify_finish(error_msg='缺少参数')
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        token = self.redis_cache.get(setting.SINA_TOKEN_KEY)
        cursor, conn = self.application.db_pool.get_conn()
        data = {'isDownloading': False}
        try:
            row_id = SearchHistoryModel.insert_record(
                keyword, start_time, end_time, cursor)
            run('nohup /code/sina/venv/bin/python3 /code/sina/sinaSpider/main.py '
                f'{keyword} {int(start_time.timestamp())} {int(end_time.timestamp())} {row_id} {token.decode()} > '
                f'/code/sina/sinaSpider/spider_nohup.log 2>&1 &',
                shell=True)
        except Exception:
            logging.error(f'数据插入失败{traceback.format_exc()}')
            return self.jsonify_finish(error_msg=u'系统繁忙')
        else:
            data['isDownloading'] = True
            data['searchId'] = row_id
            return self.jsonify_finish(is_succ=True, data=data)

    @utils.login_check
    def get(self):
        search_id = self.get_argument('searchId', '')
        if not search_id:
            return self.jsonify_finish(error_msg='缺少参数：searchId')
        cursor, conn = self.application.db_pool.get_conn()
        condition = {
            'id': search_id,
        }
        record = SearchHistoryModel.get_record(condition, cursor)
        if not record:
            return self.jsonify_finish(error_msg=u'数据不存在')
        search_id, info = record['id'], record['info']
        try:
            info = json.loads(info)
        except Exception:
            logging.error(f'info 解析失败：\n{traceback.format_exc()}')
            info = {}
        article_data = ArticleListModel.get_data_group_by_date(
            search_id, cursor)
        comment_data = CommentListModel.get_data_group_by_date(
            search_id, cursor)
        data = {
            'commentCounts': info.get('comment_counts', []),
            'articleCounts': info.get('article_counts', []),
            'articleEmotion': info.get('article_emotion', []),
            'commentEmotion': info.get('comment_emotion', []),
            'articleData': article_data,
            'commentData': comment_data,
            'articleGroup': info.get('a_group_count', []),
            'commentGroup': info.get('c_group_count', []),
            'articleCloud': f'static/search_{search_id}/article.jpg',
            'commentCloud': f'static/search_{search_id}/comment.jpg'}
        self.jsonify_finish(is_succ=True, data=data)


@router.Router('/api/v1/search-list')
class SearchListHandler(helper.ApiBaseHandler):
    @utils.login_check
    def get(self):
        page = self.get_argument('page', '')
        size = self.get_argument('size', '10')
        status = self.get_argument('status', '1')
        page = int(page) if page.isdigit() else 1
        cursor, conn = self.application.db_pool.get_conn()
        condition = {
            'status': status,
        }
        records = SearchHistoryModel.get_records(
            condition, cursor, offset=page - 1, limit=size)
        count = SearchHistoryModel.count_records(condition, cursor)
        records_data = [{
            'id': item['id'],
            'keyword': item['keyword'],
            'startTime': item['start_time'].strftime('%Y-%m-%d %H:%M:%S'),
            'endTime': item['end_time'].strftime('%Y-%m-%d %H:%M:%S')}
            for item in records]
        data = {
            'list': records_data,
            'total': count
        }
        return self.jsonify_finish(is_succ=True, data=data)


@router.Router('/api/v1/get-token')
class TokenHandler(helper.ApiBaseHandler):
    def post(self):
        try:
            data = json.loads(self.request.body)
        except Exception :
            logging.error(f'参数解析失败：{traceback.format_exc()}')
            return self.jsonify_finish(error_msg=u'参数异常')
        username = data.get('username', '')
        password = data.get('password', '')
        auth_code = data.get('authCode', '')
        resp = utils.get_sina_token(auth_code)
        data = {
            'token': '',
            'refreshToken': '',
            'expiration': 0,
            'nickName': '',
        }
        sina_token = resp.get('access_token')
        if resp and sina_token:
            expires_in = resp['expires_in']
            self.redis_cache.set(setting.SINA_TOKEN_KEY, sina_token, expires_in)
            encry_pwd = utils.encrypt_hamc_sha256(setting.SECRET_KEY, password)
            cursor, conn = self.application.db_pool.get_conn()
            user = UserModel.get_user(username, encry_pwd, cursor)
            if user:
                exp = int(time.time() + expires_in)
                token, refresh_token = utils.create_token(
                    user['id'], user['username'], exp)
                data['expiration'] = exp
                data['token'] = token
                data['refreshToken'] = refresh_token
                data['nickName'] = username
                return self.jsonify_finish(is_succ=True, data=data)
            else:
                return self.jsonify_finish(error_msg='验证失败')
        else:
            return self.jsonify_finish(is_succ=True, data=data)


@router.Router('/api/v1/refresh-token')
class RefreshTokenHandler(helper.ApiBaseHandler):

    @utils.refresh_token
    def post(self):
        if 'Authorization' in self.request.headers:
            token = self.request.headers.get('Authorization').split()[-1]
        else:
            token = self.get_argument('token', '')

        status, data = utils.verify_refresh_token(token)
        user_id = data.get('user_id')
        username = data.get('username')
        exp = int(time.time()) + 3600 * 24
        token, refresh_token = utils.create_token(user_id, username, exp)
        data = {
            'token': token,
            'refreshToken': refresh_token,
            'expiration': exp
        }
        return self.jsonify_finish(is_succ=True, data=data)


@router.Router('/api/v1/user')
class UserHandler(helper.ApiBaseHandler):
    def post(self):
        username = self.get_argument('username', '')
        password = self.get_argument('password', '')
        if not all([username, password]):
            return self.jsonify_finish(error_msg=u'参数错误')
        secret = setting.SECRET_KEY
        encry_pwd = utils.encrypt_hamc_sha256(secret, password)
        cursor, conn = self.application.db_pool.get_conn()
        try:
            UserModel.create_user(username, encry_pwd, cursor)
            conn.commit()
        except Exception:
            logging.error(f'创建用户失败 \n {traceback.format_exc()}')
            return self.jsonify_finish(error_msg='系统繁忙')
        else:
            return self.jsonify_finish(is_succ=True, error_msg='添加成功')


@router.Router('/api/v1/export-article')
class ExportArticleHandler(helper.ApiBaseHandler):
    def get(self):
        search_id = self.get_argument('searchId')
        cursor, conn = self.application.db_pool.get_conn()
        article_list = ArticleListModel.query_records_by_search_id(search_id, cursor)

        article_data = [[
            '用户名', '用户主页（网址）', '微博内容', '转发', '评论', '点赞', '时间', '微博链接',
        ]]
        for item in article_list:
            article_data.append([
                item['author'],
                item['author_url'],
                re.sub('[\n]*?', '', item['content']),
                item['reposts_count'],
                item['comments_count'],
                item['attitudes_count'],
                item['publish_time'].strftime('%Y-%m-%d %H:%M:%S'),
                item['article_url']
            ])
        utils.export_to_csv(self, '{}-article.csv'.format(search_id), article_data)


@router.Router('/api/v1/export-comment')
class ExportCommentHandler(helper.ApiBaseHandler):

    def get(self):
        search_id = self.get_argument('searchId')
        cursor, conn = self.application.db_pool.get_conn()
        comment_list = CommentListModel.query_records_by_search_id(search_id, cursor)

        comment_data = [[
            '用户名',  '用户链接', '评论内容', '时间', '点赞', '微博链接'
        ]]
        for item in comment_list:
            comment_data.append([
                item['author'],
                item['author_url'],
                re.sub('[\n]*?', '', item['content']),
                item['publish_time'].strftime('%Y-%m-%d %H:%M:%S'),
                item['like_counts'],
                item['article_url'],
            ])
        utils.export_to_csv(self, '{}-comment.csv'.format(search_id), comment_data)


@router.Router('/api/v1/label-rule')
class LabelRuleHandler(helper.ApiBaseHandler):
    @utils.login_check
    def get(self):
        page = int(self.get_argument('page', '1'))
        page_size = int(self.get_argument('pageSize', '10'))
        cursor, conn = self.application.db_pool.get_conn()
        base_data = LabelRuleModel.get_labels({}, cursor, offset=(page-1)*page_size, limit=page_size)
        count = LabelRuleModel.count_total_label({}, cursor)
        data = {
            'list': base_data,
            'total': count
        }
        return self.jsonify_finish(is_succ=True, error_msg=u'', data=data)

    @utils.login_check
    def post(self):
        try:
            data = json.loads(self.request.body)
        except Exception:
            logging.error(f'参数解析失败：{traceback.format_exc()}')
            return self.jsonify_finish(error_msg=u'参数异常')
        label = data.get('label', '')
        rule = data.get('rule', '')
        label_id = data.get('labelId', '')
        if not all([label, rule]):
            return self.jsonify_finish(error_msg=u'参数错误')
        cursor, conn = self.application.db_pool.get_conn()
        try:
            if not label_id:
                LabelRuleModel.insert_label(label, rule, cursor)
            else:
                LabelRuleModel.update_label(label_id, label, rule, cursor)
        except Exception:
            logging.error(f'规则添加失败 {traceback.format_exc()}')
            return self.jsonify_finish(error_msg=u'系统繁忙')
        else:
            return self.jsonify_finish(is_succ=True, error_msg=u'添加成功')

    @utils.login_check
    def delete(self):
        try:
            data = json.loads(self.request.body)
        except Exception:
            logging.error(f'参数解析失败：{traceback.format_exc()}')
            return self.jsonify_finish(error_msg=u'参数异常')
        label_id = data.get('labelIds')
        if not label_id:
            return self.jsonify_finish(error_msg=u'缺少参数')
        label_ids = label_id.split(',')
        cursor, conn = self.application.db_pool.get_conn()
        try:
            LabelRuleModel.del_label(label_ids, cursor)
        except Exception:
            logging.error(f'label {label_id} 删除失败， {traceback.format_exc()}')
            return self.jsonify_finish(error_msg=u'系统繁忙')
        else:
            return self.jsonify_finish(is_succ=True)


@router.Router('/api/v1/get-points')
class MapPointsHandler(helper.ApiBaseHandler):
    @utils.login_check
    def get(self):
        search_id = self.get_argument('searchId')
        if not search_id:
            return self.jsonify_finish(error_msg=u'缺少参数')
        cursor, conn = self.application.db_pool.get_conn()
        base_data = ArticleListModel.query_points_by_search_id(search_id, cursor)
        data = [[item['lng'], item['lat']]for item in base_data]
        return self.jsonify_finish(is_succ=True, data=data)