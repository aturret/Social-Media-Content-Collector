# -*- coding: UTF-8 -*-
import requests
import time
import cchardet as chardet
from lxml import etree
from collections import OrderedDict
import re
from threading import Timer
from lxml.html import tostring

myfavlist = 'https://www.douban.com/doulist/145693559/'
testurl = 'https://m.weibo.cn/status/4717569200881723 '
huginnUrl = 'https://huginn.aturret.top/users/2/web_requests/63/shelleysallfamiliesdied'

def get_selector(url, headers):
    html = requests.get(url=url, headers=headers).text
    selector = etree.HTML(html)
    return selector


class Douban(object):
    def __init__(self, url):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Cookie': '',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        self.url = url
        self.content = ''
        self.origin = ''
        self.originurl = ''
        self.title = ''
        self.aurl = ''
        self.worktitle = ''
        self.workurl = ''
        self.groupname = ''
        self.groupurl = ''

    def get_fav_list(self):
        douban = OrderedDict()
        selector = get_selector(url=self.url, headers=self.headers)
        print('self='+self.aurl)
        douban['aurl'] = selector.xpath(
            'string(//*[@class="doulist-item"][1]//*[@class="title"]/a/@href|//*[@class="doulist-item"][1]//*[@class="status-content"]/a/@href)')
        print('dict='+douban['aurl'])
        print('self='+self.aurl)
        if douban['aurl'] == self.aurl:  # 如果重复就不干了
            print('弹出')
            return '1'
        else:
            self.aurl = douban['aurl']
            # url = 'https://www.douban.com/group/topic/253423326/?_i=0339993ZD7VEW1'  # 测试语句
            url=self.aurl
            # print(selector.xpath('//*[@class="doulist-item"][1]//blockquote'))
            # print(selector.xpath('//*[@class="doulist-item"][1]//div[@class="ft"]/text()'))
            if selector.xpath('//*[@class="doulist-item"][1]//div[@class="ft"]/text()')[0].find('评语') != -1:
                douban['comment'] = re.search(pattern='(?<=(评语：)).[^(\n)]*', string=selector.xpath('string(//*[@class="doulist-item"][1]//blockquote[@class="comment"])')).group()
                print(douban['comment'])
            else:
                douban['comment'] = ''
                print('没有评语')
            if url.find('note') != -1:
                self.get_douban_note(url)
            elif url.find('book.douban.com/review') != -1:
                self.get_douban_book_review(url)
            elif url.find('movie.douban.com/review') != -1:
                self.get_douban_movie_review(url)
            elif url.find('status') != -1:
                self.get_douban_status(url)
            elif url.find('group/topic') != -1:
                self.get_douban_group_article(url)

            douban['title'] = self.title
            douban['content'] = self.content
            douban['origin'] = self.origin
            douban['originurl'] = self.originurl
            #发送给huginn
            requests.post(url=huginnUrl,data=douban)
            print('ticks')
            return '1'

    def get_douban_note(self, url):
        selector = get_selector(url, headers=self.headers)
        self.title = selector.xpath('string(//div[@id="content"]//h1)')
        self.content = str(etree.tostring(selector.xpath('//div[@id="link-report"]')[0], encoding="utf-8"),
                           encoding='utf-8')
        self.origin = selector.xpath('string(//div[@class="content"]/a)')
        self.originurl = selector.xpath('string(//div[@class="content"]/a/@href)')

    def get_douban_book_review(self, url):
        selector = get_selector(url, headers=self.headers)
        self.title = selector.xpath('string(//div[@id="content"]//h1//span)')
        self.content = str(etree.tostring(selector.xpath('//div[@id="link-report"]')[0], encoding="utf-8"),
                           encoding='utf-8')
        self.origin = selector.xpath('string(//header[@class="main-hd"]//span)')
        self.originurl = selector.xpath('string(//header[@class="main-hd"]/a/@href)')
        self.worktitle = selector.xpath('string(//header[@class="main-hd"]/a[2])')
        self.workurl = selector.xpath('string(//header[@class="main-hd"]/a[2]/@href)')

    def get_douban_movie_review(self, url):
        selector = get_selector(url, headers=self.headers)
        self.title = selector.xpath('string(//div[@id="content"]//h1//span)')
        self.content = str(etree.tostring(selector.xpath('//div[@id="link-report"]')[0], encoding="utf-8"),
                           encoding='utf-8')
        self.origin = selector.xpath('string(//header[@class="main-hd"]//span)')
        self.originurl = selector.xpath('string(//header[@class="main-hd"]/a/@href)')
        self.worktitle = selector.xpath('string(//header[@class="main-hd"]/a[2])')
        self.workurl = selector.xpath('string(//header[@class="main-hd"]/a[2]/@href)')

    def get_douban_status(self, url):
        selector = get_selector(url, headers=self.headers)
        self.content = str(etree.tostring(selector.xpath('//div[@class="status-saying"]')[0], encoding="utf-8"),
                           encoding='utf-8')
        self.origin = selector.xpath('string(//div[@class="content"]/a)')
        self.originurl = selector.xpath('string(//div[@class="content"]/a/@href)')
        self.title = self.origin + '的广播'

    def get_douban_group_article(self, url):
        selector = get_selector(url, headers=self.headers)
        self.title = selector.xpath('string(//div[@id="content"]//h1)')
        self.content = str(etree.tostring(selector.xpath('//div[@id="link-report"]')[0], encoding="utf-8"),
                           encoding='utf-8')
        self.origin = selector.xpath('string(//span[@class="from"]//a)')
        self.originurl = selector.xpath('string(//span[@class="from"]//a/@href)')
        self.groupname = selector.xpath('string(//div[@id="g-side-info"]//div[@class="title"]/a)')
        self.groupurl = selector.xpath('string(//div[@id="g-side-info"]//div[@class="title"]/a/@href)')


douban = Douban(myfavlist)

#
# def sleeptime(hour, min, sec):
#     return hour * 3600 + min * 60 + sec
#
#
# second = sleeptime(0, 0, 2)
# while 1 == 1:
#     time.sleep(second)
#     douban.get_fav_list()

# print(douban.__dict__)
# t = Timer(interval=3.0, function=)
# t.start()