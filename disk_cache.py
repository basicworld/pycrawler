# -*- encoding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
from link_crawler import link_crawler
from datetime import datetime, timedelta
import os
import shutil
import zlib
from hashlib import md5
import base64
a2b_hex = base64.binascii.a2b_hex
hexlify = base64.binascii.hexlify


md5_str = lambda x: md5(x).hexdigest()


class DiskCache:
    """
    磁盘缓存
    过期检测
    数据压缩
    """
    def __init__(self, cache_dir='cache', expires=timedelta(days=30)):
        """
        cache主目录
        过期时间
        是否压缩
        """
        self.cache_dir = cache_dir
        self.expires = expires

    def __getitem__(self, url):
        path = self.url_to_path(url)
        if os.path.exists(path):
            try:
                result = json.load(open(path))
                result['timestamp'] = datetime.strptime(result['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
                # 过期返回错误
                if self.has_expired(result['timestamp']):
                    print url, 'expired'
                    raise KeyError(url + 'has expired')
                else:
                    result['html'] = zlib.decompress(a2b_hex(result['html']))
                    return result
            except ValueError as e:
                # 数据损坏
                self.__delitem__(url)
                raise KeyError(url + 'data is broken')

        else:
            raise KeyError(url + 'does not exist')

    def __setitem__(self, url, result):
        path = self.url_to_path(url)
        folder = os.path.dirname(path)
        if not os.path.isdir(folder):
            os.makedirs(folder)


        result['html'] = hexlify(zlib.compress(result['html']))
        result['timestamp'] = str(result['timestamp']
)
        with open(path, 'wb') as f:
            json.dump(result, f)
        # 下面保证result的数据没有被改变，否则会在调用的时候出错，莫名其妙的错误
        result['html'] = zlib.decompress(a2b_hex(result['html']))
        result['timestamp'] = datetime.strptime(result['timestamp'], '%Y-%m-%d %H:%M:%S.%f')



    def __delitem__(self, url):
        path = self.url_to_path(url)
        try:
            os.remove(path)
        except OSError:
            pass

    def url_to_path(self, url):
        md5url = md5_str(url)
        return os.path.realpath(os.path.join(self.cache_dir, md5url))

    def has_expired(self, timestamp):
        return datetime.utcnow() > (timestamp + self.expires)

    def clear(self):
        """
        删除所有cache
        """
        if os.path.isdir(self.cache_dir):
            shutil.rmtree(self.cache_dir)


if __name__ == '__main__':
    from datetime import timedelta
    link_crawler('http://example.webscraping.com/', delay=3, link_regex='/(index|view)',
                 max_urls=-1, cache=DiskCache(expires=timedelta(hours=1)))
