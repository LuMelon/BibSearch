import requests
from bs4 import BeautifulSoup
import random
from UA import agents

headers={
    'User-Agent':random.choice(agents),
}

def ConstructSess():
    sess = requests.sessions()

    return sess

def ToBib(datalink, datasign, diversion):
    bib_url_format = 'http://xueshu.baidu.com/u/citation?&url={datalink}&sign={datasign}&diversion={diversion}&t=bib'
    bib_url = bib_url_format.format(datalink=datalink, datasign=datasign, diversion=diversion)
    while True:
        sess = ConstructSess()
        html = sess.get(bib_url)
        if html.status_code == 200:
            break
        elif html.status_code ==404:
            break
        else:
            continue
    soup = BeautifulSoup(html.text, 'html.parse')
    return soup.body.pre.text

def Parse(html):

    return

def Serach(title):
    search_url_format = ''
    return

