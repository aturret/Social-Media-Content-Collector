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

myfavlist = 'https://www.douban.com/doulist/145693559/'
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

