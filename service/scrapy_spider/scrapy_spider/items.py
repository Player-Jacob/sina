# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SinaSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    author = scrapy.Field()
    author_url = scrapy.Field()
    article_url = scrapy.Field()
    publish_time = scrapy.Field()
    content = scrapy.Field()
    html_content = scrapy.Field()
    search_id = scrapy.Field()
