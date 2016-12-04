# -*- encoding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo import errors as mgerrors


class MongoQueue:
    """
    >>> timeout = 1
    >>> url = 'http://example.webscraping.com'
    >>> q = MongoQueue(timeout=timeout)
    >>> q.clear() # ensure empty queue
    >>> q.push(url) # add test URL
    >>> q.peek() == q.pop() == url # pop back this URL
    True
    >>> q.repair() # immediate repair will do nothin
    >>> q.pop() # another pop should be empty
    Traceback (most recent call last):
        ...
    KeyError
    >>> q.peek()
    >>> import time; time.sleep(timeout) # wait for timeout
    >>> q.repair() # now repair will release URL
    Released: http://example.webscraping.com
    >>> q.pop() == url # pop URL again
    True
    >>> bool(q) # queue is still active while outstanding
    True
    >>> q.complete(url) # complete this URL
    >>> bool(q) # queue is not complete
    False
    """
    # """
    # 基于mongo的队列
    # 用于支持多线程
    # """

    # 可能的下载状态
    OUTSTANDING, PROCESSING, COMPLETE = range(3)

    def __init__(self, client=None, timeout=300):
        """"""
        self.client = client or MongoClient(connect=False)
        self.db = self.client.cache
        self.timeout = timeout

    def __nonzero__(self):
        """
        队列是否为空
        非空则返回True
        """
        record = self.db.crawl_queue.find_one({'status': {'$ne': self.COMPLETE}})
        return (True if record else False)
        pass

    def push(self, url):
        """将url放入队列"""
        try:
            self.db.crawl_queue.insert_one({'_id': url, 'status': self.OUTSTANDING})

        except mgerrors.DuplicateKeyError as e:
            pass

    def pop(self):
        """
        取出url则添加一个时间标签，
        """
        record = self.db.crawl_queue.find_and_modify(
            query={'status': self.OUTSTANDING},
            update={'$set': {'status': self.PROCESSING, 'timestamp': datetime.utcnow()}})
        if record:
            return record['_id']
        else:
            self.repair()
            raise KeyError()
            # return None

    def peek(self):
        """
        返回outstanding状态的id
        """
        record = self.db.crawl_queue.find_one({'status': self.OUTSTANDING})
        if record:
            return record['_id']

    def complete(self, url):
        """
        将队列状态标记为complete
        """
        self.db.crawl_queue.update_one({'_id': url}, {'$set': {'status': self.COMPLETE}})
        pass

    def repair(self):
        """
        将timeout时间内没完成的任务重置任务状态
        """
        record = self.db.crawl_queue.find_and_modify(
            query={'timestamp': {'$lt': datetime.utcnow() - timedelta(seconds=self.timeout)},
                   'status': {'$ne': self.COMPLETE}},
            update={'$set': {'status': self.OUTSTANDING}})
        if record:
            print 'Released:', record['_id']

    def clear(self):
        """
        清空爬虫队列
        """
        self.db.crawl_queue.drop()
        pass

if __name__ == '__main__':
    import doctest
    doctest.testmod()
