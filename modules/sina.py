#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/26 11:32
    author: Ghost
    desc: 
"""


class SearchHistoryModel:
    __table_name__ = 'search_history'

    @classmethod
    def insert_record(cls, keyword, start_time, end_time, db):
        sql = f"insert into {cls.__table_name__} (keyword, start_time, end_time) " \
              f"value(%s, %s, %s)"
        print(sql, 3333)
        db.execute(sql, (keyword, start_time, end_time))
        db.close()

        return db.lastrowid