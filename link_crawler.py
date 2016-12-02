# -*- encoding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import robotparser
from downloader import Downloader
import re
from lxml import etree
from purl import URL
import urlparse

same_host = lambda url1, url2: URL(url1).host() == URL(url2).host()
get_links = lambda html: etree.HTML(html).xpath('//a/@href')


def link_crawler(seed_url, link_regex=None, delay=5, max_depth=-1, max_urls=-1, user_agent='Safari',
                proxies=None, num_retries=1, scrape_callback=None, cache=None, robots_url=None):
    """
    根据给定seed_url递归爬取数据
    robots_url: 给出robotsurl 则遵守robot规则，否则不遵守
    """
    crawl_queue = [seed_url]
    seen = {seed_url: 0}  # 已爬取url和爬虫深度
    num_urls = 0  # 爬取个数
    rp = get_robots(robots_url)  # robots.txt规则
    # 定义下载器
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries,
                   cache=cache)
    while crawl_queue:
        url = crawl_queue.pop()
        depth = seen[url]
        if (not rp) or rp.can_fetch(useragent, url):
            html = D(url)
            links = []
            if scrape_callback:
                links.extend(scrape_callback(url, html) or [])
            if depth != max_depth:
                # 匹配符合条件的link
                if link_regex:
                    links.extend(link for link in get_links(html) if re.match(link_regex, link))

                # 将符合条件的link加入下载队列
                for link in links:
                    link = normalize(seed_url, link)
                    if link not in seen:
                        seen[link] = depth + 1
                        if same_host(seed_url, link):
                            crawl_queue.append(link)

            num_urls += 1
            # 达到最大爬虫数则停止
            if num_urls == max_urls:
                break
        else:
            print 'Blocked by robots.txt', url


def get_robots(robots_url):
    """
    robots.txt解析器
    """
    if robots_url:
        rp = robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp
    else:
        return None


def normalize(seed_url, link):
    """
    相对链接改为绝对连接
    去除link hash
    """
    link, _ = urlparse.urldefrag(link)
    return urlparse.urljoin(seed_url, link)

if __name__ == '__main__':
    link_crawler('http://example.webscraping.com', '/(index|view)', delay=0,
                 max_urls=15, num_retries=1, user_agent='BadCrawler')
