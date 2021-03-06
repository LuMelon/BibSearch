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

cookie_string = 'BAIDUID=C7E0EDFE16CCAEF743B88070FA7BBF94:FG=1; BIDUPSID=C7E0EDFE16CCAEF743B88070FA7BBF94; PSTM=1557821465; H_PS_PSSID=; pgv_pvi=9270152192; pgv_si=s4949040128; delPer=0; BD_HOME=0; Hm_lvt_f28578486a5410f35e6fbd0da5361e5f=1558770773; BD_CK_SAM=1; PSINO=6'
cookies = {item.split('=')[0]:item.split('=',1)[1] for item in cookie_string.split(';')}
headers={
    'User-Agent':random.choice(agents),
}

def write_failed_title_to_txt(title):
    with open("failed_title_list.txt", 'a') as f:
        f.write(title+'\n')

def write_log_file(filename, content):
    with open(filename, 'w') as fw:
        fw.write(content)


def write_bib_to_txt(bib):
    with open("bib_list.txt", 'a') as fw:
        fw.write(bib+'\n')

def ConstructSession():
    session = requests.session()
    # proxy = requests.get('http://localhost:5000/get').text  # 获取本地代理池代理
    # idx = np.random.randint(len(proxies))
    # proxy = '%s:%s' % (proxies[idx]['ip'], proxies[idx]['port'])
    # if proxies[idx]["type"] == "https":
    #     thisproxies = {'https': 'https://{}'.format(proxy)}
    # else:
    #     thisproxies = {'http': 'http://{}'.format(proxy)}
    # session.proxies = thisproxies  # 携带代理
    return session


def ToBib(datalink, datasign, diversion):
    bib_url_format = 'http://xueshu.baidu.com/u/citation?&url={datalink}&sign={datasign}&t=bib'
    bib_url = bib_url_format.format(datalink=datalink, datasign=datasign)
    print("bib_url:", bib_url)
    while True:
        sess = ConstructSession()
        html = sess.get(bib_url, headers=headers, cookies=cookies)
        print("Bib:",html.text)
        if html.status_code == 200:
            break
        elif html.status_code ==404:
            break
        else:
            continue
    return html.text

def ExtractTheSearchPage(html, title):
    soup = Soup(html.text, 'html.parser')
    paper_paras = soup.find(id="1")
    if paper_paras is not None:
        link = paper_paras['mu'].lstrip().rstrip()
        src_url = paper_paras.find(class_='c-title').a['href']
        sign = src_url.split('sc_us=')[1].split('&')[0]
        print(sign)
        diver = ''
        return True, link, sign, diver
    else:
        print("cannot parse the paper <<%s>>"%title)
        write_log_file(title, html.text)
        return False, '', '', ''

def Search(title):
    search_url_format = 'http://xueshu.baidu.com/s?wd={keywords}&sc_hit=1'
    search_url = search_url_format.format(keywords='+'.join( title.split(' ') ) )
    print("----search_url------------:", search_url)
    while True:
        sess = ConstructSession()
        try:
            html = sess.get(search_url, headers=headers, cookies=cookies)
            print(html)
        except:
            print('获取失败，准备重新获取(%s)' % title)
            time.sleep(2)
            continue
        if html.status_code == 200:
            print("-----SearchPage: 200 type handler-----")
            flag, link, sign, diver = ExtractTheSearchPage(html, title)
            if flag:
                return flag, link, sign, diver
            else:
                continue
        elif html.status_code ==404:
            print('------SearchPage: 404 type handler -------:',title)
            return False, '', '', ''

        else:
            print("what happened:", html)

def GetBibViaTitle(title):
    flag, link, sign, diver = Search(title)
    print("--------link:%s------sign:%s-------diver:%s------" % (link, sign, diver))
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
        pool1.apply_async(func=GetBibViaTitle, args=(title.rstrip('\n').rstrip(),))

    pool1.close()
    pool1.join()#必须等待所有子进程结束