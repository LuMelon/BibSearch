import requests
from UA import agents
import time
import random
from multiprocessing import Pool
import threading
import sys
import numpy as np
from proxies import proxies
from bs4 import BeautifulSoup as Soup
import urllib

headers={
    'User-Agent':random.choice(agents),
}

def ConstructSession():
    session = requests.session()
    # proxy = requests.get('http://localhost:5000/get').text  # 获取本地代理池代理
    idx = np.random.randint(len(proxies))
    proxy = '%s:%s' % (proxies[idx]['ip'], proxies[idx]['port'])

    if proxies[idx]["type"] == "https":
        thisproxies = {'https': 'https://{}'.format(proxy)}
    else:
        thisproxies = {'http': 'http://{}'.format(proxy)}
    session.proxies = thisproxies  # 携带代理
    return session


def ToBib(datalink, datasign, diversion):
    bib_url_format = 'http://xueshu.baidu.com/u/citation?&url={datalink}&sign={datasign}&diversion={diversion}&t=bib'
    bib_url = bib_url_format.format(datalink=datalink, datasign=datasign, diversion=diversion)
    while True:
        sess = ConstructSession()
        html = sess.get(bib_url)
        if html.status_code == 200:
            break
        elif html.status_code ==404:
            break
        else:
            continue
    soup = Soup(html.text, 'html.parse')
    return soup.body.pre.text

def Parse(html):

    return

def Serach(title):
    search_url_format = ''
    return


if __name__ =='__main__':
    lock = threading.Lock()

    source_kw = set( map(lambda line:line.split(':')[0], open("source_list.txt").readlines() ) )
    faied_kw = set( map(lambda line: line.split('/')[-2], open('failed_url_list.txt').readlines() ) )
    all_kw = set( map(lambda  line: line.split(':')[0], open('events_list_night.txt').readlines() ) )
    rest_kw = all_kw - source_kw - faied_kw

    pool1 = Pool(6)

    for kw in rest_kw:
        url = 'https://www.snopes.com/fact-check/%s/'%kw
        pool1.apply_async(func=get_source, args=(url,))

    pool1.close()
    pool1.join()#必须等待所有子进程结束