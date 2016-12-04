# -*- encoding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

from process_crawler import process_crawler
from mongo_cache import MongoCache
from alexa import AlaxeCallback


def test():
    start_url = 'http://www.alexa.com/topsites/global;0'
    cache = MongoCache()
    scrape_callback = AlaxeCallback(allow_domains=[start_url])
    process_crawler(start_url,
                    link_regex='/topsites/global;',
                    cache=cache, scrape_callback=scrape_callback,
                    max_threads=8, timeout=5)

if __name__ == '__main__':
    test()
