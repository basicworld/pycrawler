# -*- encoding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

from link_crawler import link_crawler
from mongo_cache import MongoCache
from lxml import etree
import json
from purl import URL


def com_alexa():
    """
    从该网址下载一些热门网址
    """
    start_url = 'http://www.alexa.com/topsites/global;0'
    scrape_callback = AlaxeCallback(allow_domains=start_url)
    link_crawler(start_url, link_regex='/topsites/global;', delay=3, only_same_host=False, save_cache=False,
                 max_urls=100, cache=MongoCache(), scrape_callback=scrape_callback,
                 timeout=3)
    del scrape_callback


class AlaxeCallback:
    def __init__(self, max_urls=1000, **kwargs):
        """
        @kwargs
        allow_domains = []  允许解析的url
        """
        self.max_urls = max_urls
        self.total_urls = []
        self.allow_domains = kwargs.get('allow_domains', [])

    def __call__(self, url, html):
        # 如果允许解析，则解析html中的url，否则返回空
        # 如果不允许解析，则只分析url并保存到总的url劣币到列表

        tree = etree.HTML(html.decode('utf8', 'ignore'))
        # print tree.xpath('//head/meta/@content')
        urls = tree.xpath('//p[@class="desc-paragraph"]/a/text()')
        urls = ['http://www.%s' % x.lower() for x in urls]
        self.total_urls.extend(urls)
        # print self.total_urls

        return (urls if self.is_url_parse_allowed(url) else [])

    def __del__(self):
        print 'urls:', len(self.total_urls)
        if self.total_urls:
            with open('top_sites_from_alexa.js', 'wb') as f:
                json.dump(self.total_urls, f, indent=True)

    def is_url_parse_allowed(self, url):
        host = URL(url).host()
        for url in self.allow_domains:
            if host in url:
                return True
        return (False if self.allow_domains else True)


if __name__ == '__main__':
    com_alexa()
