#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/21 15:43
    author: Ghost
    desc: 
"""
import json
import logging
import traceback
import datetime

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
        status = True if self.redis_cache.get(setting.SPIDER_STATUS_KEY) else False
        data = dict(status=status)
        return self.jsonify_finish(is_succ=True, data=data)


@router.Router("/api/v1/sina-search")
class ApiSinaSearchHandler(helper.ApiBaseHandler):
    def post(self, *args, **kwargs):
        keyword = self.get_argument('keyword', '')
        start_time = self.get_argument('start_time', '')
        end_time = self.get_argument('end_time', '')
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
            return self.jsonify_finish(is_succ=True, data=data)
        search_id, info = record
        article_data = ArticleListModel.get_data_group_by_date(search_id, cursor)
        comment_data = CommentListModel.get_data_group_by_date(search_id, cursor)
        data['article_data'] = [{'date': date.decode(), 'count': count}
                                for date, count in article_data]
        data['comment_data'] = [{'date': date.decode(), 'count': count}
                                for date, count in comment_data]
        data['article_cloud'] = f'static/search_{search_id}/article.png'
        data['comment_cloud'] = f'static/search_{search_id}/comment.png'
        self.jsonify_finish(is_succ=True, data=data)


@router.Router('/api/v1/search-list')
class SearchListHandler(helper.ApiBaseHandler):

    def get(self):
        page = self.get_argument('page', '')
        size = self.get_argument('size', '10')
        page = int(page) if page.isdigit() else 1
        cursor, conn = self.application.db_pool.get_conn()
        records = SearchHistoryModel.get_records(
            {}, cursor, offset=page-1, limit=size)
        count = SearchHistoryModel.count_records({}, cursor)
        records_data = [{
            'id': item[0],
            'keyword':item[1].decode(),
            'startTime': item[2].strftime('%Y-%m-%d %H:%M:%S'),
            'endTime': item[3].strftime('%Y-%m-%d %H:%M:%S')}
            for item in records]
        data = {
            'list': records_data,
            'total': count
        }
        return self.jsonify_finish(is_succ=True, data=data)