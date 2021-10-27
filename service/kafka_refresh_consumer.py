#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/25 16:15
    author: Ghost
    desc: 
"""
import traceback

from kafka_service import BaseKafkaConsumer

from config import setting
from common import utils, service_logger

logger = service_logger.Logger('kafka_refresh_consumer.log')


class KafkaRefreshConsumer(BaseKafkaConsumer):

    @staticmethod
    def handler_msg(msg):
        data = msg.value.encode()
        logger.info(f'data: {data}')
        try:
            session = utils.get_session()
            utils.refresh_cookies(session, data)
        except Exception:
            logger.info(f'刷新cookies失败 : {traceback.format_exc()}')


def main():
    consumer = KafkaRefreshConsumer(
        topic=setting.KAFKA_REFRESH_SERVICE['TOPIC'],
        group_id=setting.KAFKA_REFRESH_SERVICE['GROUP_ID'],
        bootstrap_servers=setting.KAFKA_REFRESH_SERVICE['BOOTSTRAP_SERVERS'],
        auto_offset_reset='earliest'
    )
    consumer.run()


if __name__ == '__main__':
    main()