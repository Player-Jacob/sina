#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/21 15:19
    author: Ghost
    desc: 
"""
import json
import logging
import os
from typing import Optional, Awaitable, Any
import traceback

from bugsnag.tornado import BugsnagRequestHandler
import psutil
from tornado import ioloop

from config import setting
from common import utils


class BaseRequestHandler(BugsnagRequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def _initialize(self):
        self.executor = setting.thread_executor
        self.thread_executor = setting.thread_executor
        self.process_executor = setting.process_executor
        self.io_loop = ioloop.IOLoop.current()

    def log_memory(self):
        process = psutil.Process(os.getpid())
        logging.info(
            "%s  %sMB"
            % (self.request.path, process.memory_info()[0] / (1024 * 1024))
        )

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        self.set_header("Content-Type", "application/json; charset=UTF-8")

        if (
                self.settings.get("serve_traceback")
                and "exc_info" in kwargs
                and status_code >= 500
        ):
            # in debug mode, try to send a traceback
            data = dict(
                is_succ=False,
                error_msg="   ".join(
                    traceback.format_exception(*kwargs["exc_info"])
                ),
            )
            data = json.dumps(data, ensure_ascii=False)
            self.finish(data)
            return
        else:
            data = dict(
                is_succ=False, error_msg=f""""{kwargs["exc_info"][1]}"""
            )
            data = json.dumps(data, ensure_ascii=False)
            self.finish(data)
            return

    @property
    def redis_cache(self):
        return self.application.redis_cache

    def get_current_user(self) -> Any:
        token = self.request.headers.get('Authorization').split()[-1]
        if not token:
            token = self.get_argument('token', '')
        data = utils.decrypt_token(token)
        return data.get('user_id')


class ApiBaseHandler(BaseRequestHandler):

    def set_default_headers(self):
        # origin = str(self.request.headers.get('Origin', '*'))
        # self.set_header('Access-Control-Allow-Origin', origin)
        # self.set_header('Access-Control-Allow-Methods',
        #                 'POST, PUT, GET, OPTIONS, HEAD, DELETE')
        # self.set_header('Access-Control-Max-Age', 1000)
        # self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    def prepare(self):
        super(ApiBaseHandler, self).prepare()
        logging.debug(
            "api path: {}, args: \n {} ".format(
                self.request.uri,
                list(
                    zip(
                        list(self.request.arguments.keys()),
                        list(self.request.arguments.values()),
                    )
                ),
            )
        )

    def check_xsrf_cookie(self):
        return True

    def jsonify_finish(self,
                       is_succ=False,
                       data=None,
                       code=0,
                       error_msg='',
                       ensure_ascii=False):
        if is_succ is False and code is 0:
            code = 101
        rtn = dict(is_succ=is_succ, code=code, error_msg=error_msg)
        if data is not None:
            rtn['data'] = data
        ret = json.dumps(rtn, ensure_ascii=ensure_ascii)
        return self.finish(ret)
