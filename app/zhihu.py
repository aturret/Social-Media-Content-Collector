# -*- coding: UTF-8 -*-
import requests
import time
import cchardet as chardet
from lxml import etree
from collections import OrderedDict
import re
from threading import Timer
from lxml.html import tostring
from . import util

myfavlist = 'https://zhuanlan.zhihu.com/p/449095252'
testurl = 'https://m.weibo.cn/status/4717569200881723 '
huginnUrl = ''


class Zhihu(object):
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
        zhihu = OrderedDict()
        selector = util.get_selector(url=self.url, headers=self.headers)
        print(util.local_time())
        # print(str(etree.tostring(selector.xpath('//body')[0], encoding="utf-8"),encoding='utf-8'))

    def get_article(self):
        print(str(etree.tostring(selector.xpath('//div[@class="RichText ztext Post-RichText css-hnrfcf"]')[0], encoding="utf-8"),encoding='utf-8'))

        # print(selector.xpath(''))



        # "extract": {
        #     "url": {
        #         "path": "data[0].url"
        #     },
        #     "title": {
        #         "path": "data[0].question.title"
        #     },
        #     "author": {
        #         "path": "data[0].author.name"
        #     },
        #     "author_url": {
        #         "path": "data[0].author.url"
        #     }
        # }

zhihu = Zhihu(myfavlist)
zhihu.get_fav_list()