#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/25 16:29
    author: Ghost
    desc: 
"""
import logging
import traceback

from kafka import KafkaConsumer


class BaseKafkaConsumer:
    def __init__(self, topic, group_id, bootstrap_servers, auto_offset_reset='latest'):
        self.topic = topic
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers
        self.auto_offset_reset = auto_offset_reset

    @staticmethod
    def handler_msg(msg):
        pass

    def run(self):
        try:
            consumer = KafkaConsumer(
                self.topic,
                group_id=self.group_id,
                bootstrap_servers=self.bootstrap_servers,
                auto_offset_reset=self.auto_offset_reset
            )
            for msg in consumer:
                try:
                    consumer.commit()
                    self.handler_msg(msg)
                except Exception:
                    logging.error('KafkaConsumer handler_message error, traceback: %s' % traceback.format_exc())
        except Exception:
             logging.error('KafkaConsumer error, traceback: %s' % traceback.format_exc())

