#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/21 15:43
    author: Ghost
    desc: 
"""
import json
import os
import logging
import traceback
import datetime

from tornado.web import StaticFileHandler, HTTPError

from common import helper, utils
from libs import router
from config import setting
from modules.sina import SearchHistoryModel, ArticleListModel, CommentListModel


@router.Router("/api/v1/sina-index")
class ApiSinaIndexHandler(helper.ApiBaseHandler):

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
    def get(self, *args, **kwargs):
        session = utils.get_session()
        status = utils.is_login_sina(session)
        data = dict(isLogin=status)
        return self.jsonify_finish(is_succ=True, data=data)


@router.Router("/api/v1/check-spider")
class ApiSinaCheckHandler(helper.ApiBaseHandler):
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
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S'
                                                ).strftime('%Y-%m-%d-%H')
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S'
                                              ).strftime('%Y-%m-%d-%H')
        cursor, conn = self.application.db_pool.get_conn()
        condition = {
            'keyword': keyword,
            'start_time': start_time,
            'end_time': end_time
        }
        record = SearchHistoryModel.get_record(condition, cursor)
        data = {'isDownloading': False}
        if not record:
            try:
                row_id = SearchHistoryModel.insert_record(
                    keyword, start_time, end_time, cursor)
            except Exception:
                logging.error(f'数据插入失败{traceback.format_exc()}')
                return self.jsonify_finish(error_msg=u'系统繁忙')
            else:
                conn.commit()
                spider_data = {
                    'keyword': keyword,
                    'start_time': start_time,
                    'end_time': end_time,
                    'search_id': row_id
                }
                self.redis_cache.rpush('start_urls', json.dumps(spider_data))
            data['isDownloading'] = True
            data['searchId'] = row_id
            return self.jsonify_finish(is_succ=True, data=data)
        return self.jsonify_finish(error_msg=u'数据已经存在')

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
        search_id, info = record
        try:
            info = json.loads(info)
        except Exception:
            logging.error(f'info 解析失败：\n{traceback.format_exc()}')
            info = {}
        article_data = ArticleListModel.get_data_group_by_date(
            search_id, cursor)
        comment_data = CommentListModel.get_data_group_by_date(
            search_id, cursor)
        comment_count_list = sorted(info.get('comment_counts', {}).items(),
                                    key=lambda kv: (kv[1], kv[0]), reverse=True)
        article_counts_list = sorted(info.get('article_counts', {}).items(),
                                    key=lambda kv: (kv[1], kv[0]), reverse=True)
        data = {
            'commentCounts': [{'word': item[0], 'count': item[1]}
                              for item in comment_count_list[:20]],
            'articleCounts': [{'word': item[0], 'count': item[1]}
                              for item in article_counts_list[:20]],
            'articleEmotion': info.get('article_emotion', {}),
            'commentEmotion': info.get('comment_emotion', {}),
            'articleData': [{'date': date.decode(), 'count': count}
                            for date, count in article_data],
            'commentData': [{'date': date.decode(), 'count': count}
                            for date, count in comment_data],
            'articleCloud': f'static/search_{search_id}/article.jpg',
            'commentCloud': f'static/search_{search_id}/comment.jpg'}
        self.jsonify_finish(is_succ=True, data=data)


@router.Router('/api/v1/search-list')
class SearchListHandler(helper.ApiBaseHandler):

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
            'id': item[0],
            'keyword': item[1].decode(),
            'startTime': item[2].strftime('%Y-%m-%d %H:%M:%S'),
            'endTime': item[3].strftime('%Y-%m-%d %H:%M:%S')}
            for item in records]
        data = {
            'list': records_data,
            'total': count
        }
        return self.jsonify_finish(is_succ=True, data=data)


class FileFallbackHandler(StaticFileHandler):
    def validate_absolute_path(self, root, absolute_path):
        try:
            absolute_path = super().validate_absolute_path(root, absolute_path)
        except HTTPError:
            root = os.path.abspath(root)
            absolute_path = os.path.join(root, self.default_filename)
        return absolute_path