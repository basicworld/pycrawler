# -*- encoding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

from threaded_crawler import threaded_crawler
from mongo_cache import MongoCache
from alexa import AlaxeCallback


def test(max_threads):
    start_url = 'http://www.alexa.com/topsites/global;0'
    scrape_callback = AlaxeCallback(allow_domains=[start_url])
    cache = MongoCache()
    # start_url = 'http://www.eastday.com'
    # start_url = 'http://www.qq.com'

    threaded_crawler(start_url, link_regex='/topsites/global;', cache=cache, scrape_callback=scrape_callback,
                     max_threads=max_threads, timeout=5)

if __name__ == '__main__':
    test(8)
