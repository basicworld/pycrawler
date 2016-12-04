# -*- encoding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import threading
from purl import URL
from downloader import Downloader
import urlparse
import time
import os
import re
from lxml import etree
from mongo_queue import MongoQueue

BASEDIR = (os.path.dirname(os.path.abspath(__file__)))
SLEEP_TIME = 1
get_links = lambda html: etree.HTML(html).xpath('//a/@href')


def threaded_crawler(seed_url, link_regex=None, delay=1, cache=None, scrape_callback=None, user_agent='Safari',
                     proxies=None, num_retries=1, max_threads=10, timeout=60):
    """
    多线程爬虫
    多个线程处理一个队列
    使用mongo作为队列
    """
    # crawl_queue = [seed_url]
    crawl_queue = MongoQueue()
    crawl_queue.clear()
    crawl_queue.push(seed_url)

    # seen = set([seed_url])

    # 黑名单网站
    block_filename = os.path.join(BASEDIR, 'blocked_urls.txt')
    blocked_urls = [i.strip() for i in open(block_filename) if i.strip()] \
        if os.path.isfile(block_filename) else []
    # save_cache=False为测试需要
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries,
                   timeout=timeout, cache=cache, save_cache=False, blocked_urls=blocked_urls)

    def process_queue():
        while 1:
            try:
                url = crawl_queue.pop()
            except (IndexError, KeyError):
                # 队列为空则停止
                break
            else:
                html = D(url) if url else None
                if html and scrape_callback:
                    try:
                        links = scrape_callback(url, html) or []
                        if link_regex:
                            links.extend(link for link in get_links(html)
                                         if re.match(link_regex, link))

                    except Exception as e:
                        print 'Error in callback for: {}: {}'.format(url, e)
                    else:
                        for link in links:
                            link = normalize(seed_url, link)
                            crawl_queue.push(link)  # 入列
                            # if link not in seen:
                            #     seen.add(link)
                # print html
                # if html:
                #     # 标记为已完成
                #     crawl_queue.complete(url)
                crawl_queue.complete(url)

    threads = []
    while threads or crawl_queue:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < max_threads and crawl_queue:
            thread = threading.Thread(target=process_queue)
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)
        time.sleep(SLEEP_TIME)
    # process_queue()


def normalize(seed_url, link):
    link, _ = urlparse.urldefrag(link)
    return urlparse.urljoin(seed_url, link)
