# -*- encoding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import socket
import requests
import time
import random
from datetime import datetime, timedelta
from purl import URL
from hashlib import md5

DEFAULT_DELAY = 5
DEFAULT_AGENT = 'Safari'
DEFAULT_RETRIES = 1
DEFAULT_TIMEOUT = 60


class Downloader:
    """
    网页下载器
    缓存采用MD5存储
    """
    def __init__(self, delay=DEFAULT_DELAY, user_agent=DEFAULT_AGENT, proxies=None,
                 num_retries=DEFAULT_RETRIES, timeout=DEFAULT_TIMEOUT, cache=None,
                 opener = None):
        socket.setdefaulttimeout(timeout)
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.proxies = proxies
        self.num_retries = opener
        self.cache = cache
        self.num_retries = num_retries

        pass

    def __call__(self, url):
        result = None
        if self.cache:
            # 有缓存，尝试调取缓存
            try:
                result = self.cache[url]
            except KeyError:
                # 没有缓存
                pass
            else:
                if self.num_retries > 0 and 500 <= result['code'] < 600:
                    # 服务器错误，所以放弃缓存
                    result = None

        if not result:
            # 没有缓存， 需要下载
            self.throttle.wait(url)  # 根据url进行等待
            proxy = random.choice(self.proxies) if self.proxies else None
            headers = {'User-agent': self.user_agent}
            result = self.download(url, headers, num_retries=self.num_retries, proxy=proxy)
            if self.cache:
                self.cache[url] = result

        return result['html']


    def download(self, url, headers, num_retries, proxy=None, data=None):
        print 'Download:', url
        html = ''
        resp = requests.get(url, headers=headers, proxies=proxy)
        code = resp.status_code
        if resp.status_code == 200:
            html = resp.content
        if num_retries > 0 and 500 <= resp.status_code < 600:
            return self.download(url, headers, num_retries-1, proxy)

        return {'html': html, 'code': code, 'timestamp':str(datetime.utcnow())}



class Throttle:
    """
    对同一domain的url设置延迟下载
    """
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}
        pass

    def wait(self, url):
        """
        如果最近下载过该网站则延迟下载
        """
        domain = URL(url).host()
        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)

        self.domains[domain] = datetime.now()
        pass
