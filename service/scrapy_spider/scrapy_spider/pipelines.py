# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime
import json

import pymysql

from config import setting


class SinaSpiderPipeline:
    def __init__(self):
        self.db = self.get_db()
        self.cursor = self.db.cursor()
        self.file = open('weibo.json', 'w')

    @staticmethod
    def get_db():
        adb_params = dict(
            host=setting.MYSQL_SETTING['HOST'],
            database=setting.MYSQL_SETTING['NAME'],
            user=setting.MYSQL_SETTING['USER'],
            password=setting.MYSQL_SETTING['PASSWORD'],
            port=setting.MYSQL_SETTING['PORT']
        )
        return pymysql.connect(**adb_params)

    def process_item(self, item, spider):
        result = {}
        for k, v in item.items():
            if isinstance(v, datetime.datetime):
                v = v.strftime('%Y-%m-%d %H:%M:%S')
            result[k] = v
        self.file.write(json.dumps(result)+',\n')
        self.file.flush()
        # sql = 'insert into sina_weibo (author, author_url, publish_time, article_url, content, html_content) value(%s, %s, %s, %s, %s, %s)'
        # self.cursor.execute(sql, (item['author'], item['author_url'],
        #                           item['publish_time'],
        #                           item['article_url'], item['content'],
        #                           item['html_content']))
        # # print(self.cursor.execute('select * from sina_weibo'))
        # self.db.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.db.close()
        self.file.close()