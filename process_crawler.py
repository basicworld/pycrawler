# -*- encoding:utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import multiprocessing
from threaded_crawler import threaded_crawler


def process_crawler(args, **kwargs):
    num_cpus = multiprocessing.cpu_count()
    print 'Starting {} processes'.format(num_cpus-1)
    processes = []
    for i in range(num_cpus):
        p = multiprocessing.Process(target=threaded_crawler, args=[args], kwargs=kwargs)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
