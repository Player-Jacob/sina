import datetime
import logging
import re
import traceback
from http import cookiejar
from urllib import parse
import time

import scrapy
from scrapy.http import Request

from config import setting
from service.scrapy_spider.scrapy_spider.items import SinaSpiderItem


class SinaSpider(scrapy.Spider):
    name = 'sina_spider'
    allowed_domains = ['weibo.com']
    start_urls = [setting.SINA_ACCOUNT_URL.format(int(time.time() * 1000))]
    id = 0

    def __init__(self, key_word=None, start='', end_time='',
                 search_id: int = 0, *args, **kwargs):
        super(SinaSpider, self).__init__(*args, **kwargs)
        self.urls = self.generate_url(key_word, start, end_time)
        self.search_id = search_id

    def start_requests(self):
        headers = setting.HEADERS
        cookies = self.get_cookies()
        for url in self.start_urls:
            yield Request(url, headers=headers, cookies=cookies)

    @staticmethod
    def get_cookies():
        cookies_path = setting.COOKIE_PATH
        cookies = cookiejar.LWPCookieJar(cookies_path)
        cookies.load(ignore_discard=True)
        return {item.name: item.value for item in cookies}

    def parse(self, response: scrapy.http.Response, **kwargs):

        next_urls = response.xpath('//span[@class="list"]//li/a/@href')
        if not next_urls:
            for url in self.urls:
                yield Request(url, callback=self.parse)

        for next_url in next_urls:
            yield Request(response.urljoin(next_url.get()), callback=self.parse)

        for item in response.xpath(
                '//div[@id="pl_feedlist_index"]//div[@class="card-wrap"]'):
            item_resp = scrapy.http.HtmlResponse(response.url,
                                                 body=item.get().encode())

            author = item_resp.xpath('//a[@class="name"]/@nick-name').extract()
            author_url = item_resp.xpath('//a[@class="name"]/@href').extract()
            publish_time = item_resp.xpath(
                '//p[@class="from"]/a/text()').extract()
            short_content = item_resp.xpath(
                '//p[@node-type="feed_list_content"]').extract()
            long_content = item_resp.xpath(
                '//p[@node-type="feed_list_content_full"]').extract()
            media_context = item_resp.xpath(
                '//div[@node-type="feed_list_media_prev"]').extract()
            article_url = item_resp.xpath(
                '//p[@class="from"]/a[1]/@href').extract()
            html_content = (long_content if long_content else short_content) + media_context
            html_content = ''.join(html_content) if html_content else ''
            content = re.sub('<[\s\S]*?>', '', html_content).strip()

            spider_itme = SinaSpiderItem()
            spider_itme['author'] = author[0] if author else ''
            spider_itme['author_url'] = item_resp.urljoin(
                author_url[0]) if author_url else ''
            spider_itme['publish_time'] = self._parse_time(
                publish_time[0] if publish_time else '')
            spider_itme['article_url'] = item_resp.urljoin(
                article_url[0]) if article_url else ''
            spider_itme['content'] = content
            spider_itme['html_content'] = html_content
            spider_itme['search_id'] = self.search_id
            yield spider_itme

    @staticmethod
    def _parse_time(time_str: str):
        """
        解析文本时间
        """
        now = datetime.datetime.now()
        time_str = time_str.strip()
        try:
            if '前' in time_str:
                num = re.findall('(\d+)', time_str)
                num = int(num[0]) if num else 0
                if '秒前' in time_str:
                    date_time = now - datetime.timedelta(seconds=num)
                elif '分钟前' in time_str:
                    date_time = now - datetime.timedelta(minutes=num)
                elif '小时前' in time_str:
                    date_time = now - datetime.timedelta(hours=num)
                else:
                    date_time = now
            elif '今天' in time_str:
                today = now.strftime('%Y-%m-%d')
                time_str = re.findall('(\d+:\d+)', time_str)
                time_str = time_str[0] if time_str else 0
                new_time_str = f"{today} {time_str}"
                date_time = datetime.datetime.strptime(
                    new_time_str, '%Y-%m-%d %H:%M')
            elif '年' in time_str:
                date_time = datetime.datetime.strptime(
                    time_str, '%Y年%m月%d日 %H:%M')
            else:
                year = now.strftime('%Y')
                time_str = f"{year}年{time_str}"
                date_time = datetime.datetime.strptime(
                    time_str, '%Y年%m月%d日 %H:%M')
        except Exception:
            logging.error(f'parse time error: {traceback.format_exc()}')
            date_time = now
        return date_time

    @staticmethod
    def generate_url(key_word: str, start_time: str, end_time: str):
        """
        生成url
        """
        params = {
            'q': key_word,
            'typeall': 1,
            'timescope': f'custom:{start_time}:{end_time}',
            'suball': 1,
            'Refer': 'g'
        }
        base_url = f"https://s.weibo.com/weibo?{parse.urlencode(params, safe=':')}"
        return [base_url]


def start(key_word: str, start_time: str, end_time: str, search_id):
    import sys
    from scrapy import cmdline
    sys.argv = ['scrapy', 'crawl', 'sina_spider', '-a', f'key_word={key_word}',
                '-a' f'start_time={start_time}', '-a' f'end_time={end_time}',
                '-a', f'search_id={search_id}']
    cmdline.execute()


if __name__ == '__main__':
    key = '疫情'
    start_time = '2021-10-15-10'
    end_time = '2021-10-16-14'
    search_id = 20
    start(key, start_time, end_time, search_id)
