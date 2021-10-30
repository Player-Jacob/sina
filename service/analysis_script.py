#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/29 19:12
    author: Ghost
    desc: 
"""
import re

import jieba
import numpy as np
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS
import matplotlib.pyplot as plt

from common.database import get_conn
conn_pool = get_conn()
cursor, conn = conn_pool.get_conn()


def get_article_data(search_id, table='article_list'):
    sql = f"select content from {table} where search_id = {search_id}"
    cursor.execute(sql)
    return [item[0].decode() for item in cursor.fetchall()]


def get_data(search_id, table='article_list'):
    content_list = get_article_data(search_id, table)
    content = re.sub('\[.*?\]|http[:/\.\w]*|\s', '', ' '.join(content_list))
    return ' '.join(jieba.lcut(content))


def generate_word_cloud(search_id, table):
    space_list = get_data(search_id, table)
    print(space_list)
    # back_ground = np.array(Image.open('img.png'))
    wc = WordCloud(width=1400, height=2200,
                   background_color='white',
                   mode='RGB',
                   # mask=back_ground,  # 添加蒙版，生成指定形状的词云，并且词云图的颜色可从蒙版里提取
                   max_words=500,
                   stopwords=STOPWORDS.add('微博'),  # 内置的屏蔽词,并添加自己设置的词语
                   font_path='AaBanRuoKaiShu-2.ttf',
                   max_font_size=150,
                   relative_scaling=0.6,  # 设置字体大小与词频的关联程度为0.4
                   random_state=50,
                   scale=2
                   ).generate(space_list)
    # image_color = ImageColorGenerator(back_ground)  # 设置生成词云的颜色，如去掉这两行则字体为默认颜色
    # wc.recolor(color_func=image_color)

    plt.imshow(wc)  # 显示词云
    plt.axis('off')  # 关闭x,y轴
    plt.show()  # 显示
    wc.to_file('test1_ciyun.jpg')  # 保存词云图


if __name__ == '__main__':
    # print(get_data(20))
    generate_word_cloud(20, 'article_list')