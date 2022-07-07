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

        sql = f"select id, info, keyword from {cls.__table__} {where}"
        db.execute(sql, values)
        return db.fetchone()

    @classmethod
    def get_records(cls, condition, db, filed='id', sort='desc', offset=0, limit=10):
        keys, values = [], []
        for k, v in condition.items():
            keys.append(f"{k}=%s")
            values.append(v)

        where = ""
        if keys:
            where = 'where '+' and '.join(keys)

        sql = f"select id, keyword, start_time, end_time from {cls.__table__} " \
              f"{where} order by {filed} {sort} limit {offset}, {limit}"
        db.execute(sql, values)
        return db.fetchall()

    @classmethod
    def count_records(cls, condition, db):
        keys, values = [], []
        for k, v in condition.items():
            keys.append(f"{k}=%s")
            values.append(v)

        where = ""
        if keys:
            where = 'where '+' and '.join(keys)

        sql = f"select count(id) `count` from {cls.__table__} {where}"
        db.execute(sql, values)
        return db.fetchone()['count']

    @classmethod
    def drop_record(cls, search_id, db):
        sql = "delete from search_history where id = %s"
        return db.execute(sql, [search_id])


class ArticleListModel:
    __table__ = 'article_list'

    @classmethod
    def get_data_group_by_date(cls, search_id, db):
        sql = "select DATE_FORMAT(publish_time,'%Y-%m-%d %H') `date`,count(id) `count`" \
              f" from {cls.__table__} where search_id = {search_id} " \
              f"group by `date` order by `date`"
        db.execute(sql)
        return db.fetchall()

    @classmethod
    def query_records_by_search_id(cls, search_id, db):
        sql = f"select * from {cls.__table__} where search_id = %s"
        db.execute(sql, (search_id,))
        return db.fetchall()

    @classmethod
    def query_points_by_search_id(cls, search_id, db):
        sql = f"select lng, lat from {cls.__table__} where search_id = %s and lng != ''"
        db.execute(sql, (search_id,))
        return db.fetchall()


class CommentListModel:
    __table__ = 'comment_list'

    @classmethod
    def get_data_group_by_date(cls, search_id, db):
        sql = "select DATE_FORMAT(publish_time,'%Y-%m-%d %H') `date`, count(id) `count`" \
              f" from {cls.__table__} where search_id = {search_id} " \
              f"group by `date` order by `date`"
        db.execute(sql)
        return db.fetchall()

    @classmethod
    def query_records_by_search_id(cls, search_id, db):
        sql = f"select * from {cls.__table__} where search_id = %s"
        db.execute(sql, (search_id,))
        return db.fetchall()

    @classmethod
    def query_points_by_search_id(cls, search_id, db):
        sql = f"select lng, lat from {cls.__table__} where search_id = %s and lng != ''"
        db.execute(sql, (search_id,))
        return db.fetchall()


class UserModel:
    __table__ = 'user'

    @classmethod
    def create_user(cls, username, password, db):
        sql = f'insert into {cls.__table__}(username, `password`) value (%s, %s)'
        db.execute(sql, (username, password))
        return db.lastrowid

    @classmethod
    def get_user(cls, username, password, db):
        sql = f'select * from {cls.__table__} where username=%s and `password`=%s'
        count = db.execute(sql, (username, password))
        return db.fetchone()

    @classmethod
    def get_user_by_id(cls, user_id, db):
        sql = f'select * from {cls.__table__} where id=%s'
        count = db.execute(sql, (user_id,))
        return db.fetchone()


class LabelRuleModel:
    __table__ = 'label_list'

    @classmethod
    def insert_label(cls, label, rule, db):
        sql = f"insert into {cls.__table__} (label, rule) value (%s, %s);"
        db.execute(sql, [label, rule])
        return db.lastrowid

    @classmethod
    def update_label(cls, label_id, label, rule, db):
        sql = f"update {cls.__table__} set label=%s, rule=%s where id=%s and is_del=0"
        db.execute(sql, [label, rule, label_id])
        return db.lastrowid

    @classmethod
    def del_label(cls, label_id, db):
        sql = f"update {cls.__table__} set is_del=1 where id in %s and is_del=0"
        db.execute(sql, [label_id])

    @classmethod
    def get_labels(cls, condition: dict, db, filed='id', sort='desc', offset=0, limit=10):
        condition.setdefault('is_del', 0)
        keys, values = [], []
        for k, v in condition.items():
            if k == 'label':
                keys.append(f"label like \'%%{str(v)}%%\'")
            else:
                keys.append(f"{k}=%s")
                values.append(v)

        where = ""
        if keys:
            where = 'where ' + ' and '.join(keys)

        sql = f"select id labelId, label, rule from {cls.__table__} " \
              f"{where} order by {filed} {sort} limit {offset}, {limit}"
        db.execute(sql, values)
        return db.fetchall()

    @classmethod
    def count_total_label(cls, condition: dict, db):
        condition.setdefault('is_del', 0)
        keys, values = [], []
        for k, v in condition.items():
            if k == 'label':
                keys.append(f"label like \'%%{str(v)}%%\'")
            else:
                keys.append(f"{k}=%s")
                values.append(v)

        where = ""
        if keys:
            where = 'where ' + ' and '.join(keys)
        sql = f"select count(id) `count` from {cls.__table__} {where}"
        db.execute(sql, values)
        return db.fetchone()['count']