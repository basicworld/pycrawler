# -*- encoding:utf8 -*-
"""
使用mongodb作为缓存器
测试本地缓存
"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import json
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.binary import Binary
import zlib
import time

class MongoCache:
    def __init__(self, client=None, expires=timedelta(days=30)):
        self.client = client or MongoClient()

        # 使用cache作为缓存的collection
        self.db = self.client.cache
        # cache过期后自动删除
        self.db.webpage.create_index('timestamp', expireAfterSeconds=expires.total_seconds())

    def __contains__(self, url):
        try:
            self[url]
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, url):
        result = self.db.webpage.find_one({'_id': url})
        if result:
            result['html'] = zlib.decompress(result['html'])
            return result
        else:
            raise KeyError(url + 'does not exists')
        pass

    def __setitem__(self, url, result):
        result['html'] = Binary(zlib.compress(result['html']))
        self.db.webpage.replace_one({'_id': url}, result, upsert=True)
        result['html'] = zlib.decompress(result['html'])


    def clear(self):
        self.db.webpage.drop()


def test(timesleep=60):
    cache = MongoCache(expires=timedelta())
    time.sleep(timesleep)
    cache['http://www.baidu.com'] = {'html': '<p>asd</p>', 'timestamp': str(datetime.utcnow())}
    print cache['http://www.baidu.com']

if __name__ == '__main__':
    from link_crawler import link_crawler
    link_crawler('http://example.webscraping.com/', delay=3, link_regex='/(index|view)',
                 max_urls=-1, cache=MongoCache())
