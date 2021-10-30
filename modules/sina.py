#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/26 11:32
    author: Ghost
    desc: 
"""


class SearchHistoryModel:
    __table__ = 'search_history'

    @classmethod
    def insert_record(cls, keyword, start_time, end_time, db):
        sql = f"insert into {cls.__table__} (keyword, start_time, end_time) " \
              f"value(%s, %s, %s)"
        print(sql, 3333)
        db.execute(sql, (keyword, start_time, end_time))
        db.close()

        return db.lastrowid

    @classmethod
    def get_record(cls, condition, db):
        keys, values = [], []
        for k, v in condition.items():
            keys.append(f"{k}=%s")
            values.append(v)

        where = ""
        if keys:
            where = 'where '+' and '.join(keys)

        sql = f"select id, info from {cls.__table__} {where}"
        db.execute(sql, values)
        return db.fetchone()


class ArticleListModel:
    __table__ = 'article_list'

    @classmethod
    def get_data_group_by_date(cls, search_id, db):
        sql = "select DATE_FORMAT(publish_time,'%Y-%m-%d %H') days,count(id)" \
              f" from {cls.__table__} where search_id = {search_id} " \
              f"group by days order by days"
        db.execute(sql)
        return db.fetchall()


class CommentListModel:
    __table__ = 'comment_list'

    @classmethod
    def get_data_group_by_date(cls, search_id, db):
        sql = "select DATE_FORMAT(publish_time,'%Y-%m-%d %H') days,count(id)" \
              f" from {cls.__table__} where search_id = {search_id} " \
              f"group by days order by days"
        db.execute(sql)
        return db.fetchall()