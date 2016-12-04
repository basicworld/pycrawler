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
import chardet

DEFAULT_DELAY = 5
DEFAULT_AGENT = 'Safari'
DEFAULT_RETRIES = 1
DEFAULT_TIMEOUT = 10


class Downloader:
    """
    网页下载器
    缓存采用MD5存储
    """
    def __init__(self, delay=DEFAULT_DELAY, user_agent=DEFAULT_AGENT, proxies=None,
                 num_retries=DEFAULT_RETRIES, timeout=DEFAULT_TIMEOUT, cache=None,
                 opener = None, save_cache=True, **kwargs):
        """
        @kwargs
        blocked_urls = [] 被屏蔽网址的关键字列表，用于加入爬虫黑名单
        """
        # socket.setdefaulttimeout(timeout)
        self.timeout = timeout
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.proxies = proxies
        # self.num_retries = opener
        self.cache = cache
        self.save_cache = save_cache
        self.num_retries = num_retries
        self.blocked_urls = kwargs.get('blocked_urls', [])

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
            result = self.download(url, headers, num_retries=self.num_retries, proxy=proxy,
                                   timeout=self.timeout)
            if result and self.save_cache and self.cache:
                # 有返回内容，且需要保存cache，且有缓存 才保存
                self.cache[url] = result

        return (result['html'] if result else None)


    def download(self, url, headers, num_retries, proxy=None, data=None, timeout=60):
        if self.is_blocked_site(url):
            print 'Blocked: %s' % url
            return {'html': 'Blocked url', 'code': 408, 'timestamp': datetime.utcnow()}

        print 'Download:', url
        html = ''
        code = 408  # init
        # 这里的timeout为测试使用，正常情况下需要去掉
        try:
            resp = requests.get(url, headers=headers, proxies=proxy, timeout=self.timeout)
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
            print 'Timeout[%s seconds]: %s' % (timeout, url)
            html = 'Request timeout'
            code = 408
        except requests.exceptions.ConnectionError:
            # 连接错误， 重试一次
            # pass
            if num_retries > 0:
                return self.download(url, headers, num_retries-1, proxy, timeout=self.timeout)
        else:
            code = resp.status_code
            if resp.status_code == 200:
                html = self.utf8_encode(resp.content)
            if num_retries > 0 and 500 <= resp.status_code < 600:
                return self.download(url, headers, num_retries-1, proxy, timeout=self.timeout)
        return {'html': html, 'code': code, 'timestamp': datetime.utcnow()}

    def is_blocked_site(self, url):
        # print url, self.blocked_urls
        for site in self.blocked_urls:
            if site in URL(url).host():
                return True
        return False

    @staticmethod
    def utf8_encode(html):
        # # 添加中文编码解析, 保证输出utf8
        code_detect = chardet.detect(html)
        # print code_detect
        chinese_encode = ['gbk', 'gb2312']
        if code_detect['encoding'].lower() in chinese_encode:
            first_encode = chinese_encode.index(code_detect['encoding'].lower())
            try:
                html = html.decode(chinese_encode[first_encode]).encode('utf8')
            except UnicodeDecodeError:
                html = html.decode(chinese_encode[1 - first_encode]).encode('utf8')

        else:
            html = html.decode(code_detect['encoding']).encode('utf8')
        return html



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
