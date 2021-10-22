from http import cookiejar

import scrapy

from scrapy.http import Request
from config import setting


class SinaSpiderSpider(scrapy.Spider):
    name = 'sina_spider'
    allowed_domains = ['weibo.com', 'httpbin.org']
    start_urls = [
        'https://httpbin.org/get']

    # def __init__(self, start_urls, *args, **kwargs):
    #     super(SinaSpiderSpider, self).__init__(*args, **kwargs)
    #     self.start_urls = start_urls

    def start_requests(self):
        headers = setting.HEADERS
        cookies = self.get_cookies()
        for url in self.start_urls:
            yield Request(url, dont_filter=True, headers=headers, cookies=cookies)

    @staticmethod
    def get_cookies():
        cookies_path = setting.COOKIE_PATH
        cookies = cookiejar.LWPCookieJar(cookies_path)
        cookies.load(ignore_discard=True)
        return {item.name: item.value for item in cookies}

    def parse(self, response, **kwargs):
        print(response.request.headers)
        print(response.json())
        pass



if __name__ == '__main__':
    import sys
    from scrapy import cmdline

    sys.argv = ['scrapy', 'crawl', 'sina_spider']
    cmdline.execute()

