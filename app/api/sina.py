#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/21 15:43
    author: Ghost
    desc: 
"""
import json
import logging

from common import helper, utils
from libs import router


@router.Router("/api/v1/sina-index")
class ApiSinaIndexHandler(helper.ApiBaseHandler):
    def get(self, *args, **kwargs):
        session = utils.get_session()
        status = utils.is_login_sina(session)
        if not status:
            qr_id, image = utils.get_qr_code(session)
            logging.info("qr_id: {}, image: {}".format(qr_id, image))
            data = dict(isLogin=status, image=image)
        else:
            data = dict(isLogin=status)
        return self.jsonify_finish(is_succ=True, data=data)


@router.Router("/api/v1/sina-search")
class ApiSinaSearchHandler(helper.ApiBaseHandler):
    def get(self, *args, **kwargs):
        key_word = self.get_argument('keyword', '')
        start_time = self.get_argument('start_time', '')
        end_time = self.get_argument('end_time', '')