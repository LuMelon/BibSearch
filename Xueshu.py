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

def write_failed_title_to_txt(title):
    with open("failed_title_list.txt", 'a') as f:
        f.write(title+'\n')

def write_bib_to_txt(bib):
    with open("bib_list.txt", 'a') as fw:
        fw.write(bib)

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
    return html.text

def ExtractTheSearchPage(html, title):
    soup = Soup(html.text, 'html.parser')
    flag = False
    link = ''
    sign = ''
    diver = ''
    for i in range(5): #matching the fist 5 results
        paper = soup.find(id="%d"%i)
        if paper.div.h3.a.text == title:
            flag =True
            paras = list(paper.children)[-2]
            link = paras['url']
            sign = paras['longsign']
            diver = paras['diversion']
            break
    return flag, link, sign, diver

def Serach(title):
    search_url_format = 'http://xueshu.baidu.com/s?wd={keywords}'
    search_url = search_url_format.format(keywords='+'.join( title.split(' ') ) )
    while True:
        sess = ConstructSession()
        html = sess.get(search_url, headers=headers)
        try:
            html = sess.get(url, headers=headers)
            print(html)
        except:
            print('获取失败，准备重新获取(%s)' % title)
            time.sleep(2)
            continue
        if html.status_code == 200:
            print("-----SearchPage: 200 type handler-----")
            return ExtractTheSearchPage(html)
        elif html.status_code ==404:
            print('------SearchPage: 404 type handler -------:',title)
            return False, '', '', ''

def GetBibViaTitle(title):
    flag, link, sign, diver = Serach(title)
    if not flag:
        global failed_Write_lock
        faied_Write_lock.acquire()
        write_failed_title_to_txt(title)
        failed_Write_lock.release()
    else:
        bib = ToBib(link, sign, diver)
        global bib_Write_lock
        bib_Write_lock.acquire()
        write_bib_to_txt(bib)
        bib_Write_lock.release()


if __name__ =='__main__':
    faied_Write_lock = threading.Lock()
    bib_Write_lock = threading.Lock()

    paper_list = open("paper_list.txt").readlines()

    pool1 = Pool(6)

    for title in paper_list:
        pool1.apply_async(func=GetBibViaTitle, args=(title,))

    pool1.close()
    pool1.join()#必须等待所有子进程结束