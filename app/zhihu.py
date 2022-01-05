# -*- coding: UTF-8 -*-
import requests
import time
import cchardet as chardet
from lxml import etree
from lxml import html
from collections import OrderedDict
import re
from . import util
from html_sanitizer import Sanitizer

favurl = 'https://www.zhihu.com/pin/1457225488036573184'
testurl = 'https://m.weibo.cn/status/4717569200881723 '
huginnUrl = 'https://huginn.aturret.top/users/2/web_requests/67/shelleyisanoobplayer'


class Zhihu(object):
    def __init__(self, favurl,url):
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
        self.favurl = favurl
        self.question = ''
        self.workurl = ''
        self.groupname = ''
        self.groupurl = ''
        self.retweet_html = ''

    def get_fav_item(self):
        zhihu = OrderedDict()
        # selector = util.get_selector(url=self.url, headers=self.headers)
        print(util.local_time())
        url = self.url
        # print(str(etree.tostring(selector.xpath('//body')[0], encoding="utf-8"),encoding='utf-8'))
        if url.find('zhuanlan.zhihu.com') != -1:
            self.get_zhihu_article()
        elif url.find('answer') != -1:
            self.get_zhihu_answer()
        elif url.find('zhihu.com/pin/') != -1:
            self.get_zhihu_status()
        # elif url.find('status') != -1:
        #     self.get_douban_status(url)
        # elif url.find('group/topic') != -1:
        #     self.get_douban_group_article(url)
        print(self.__dict__)  # 测试调试
        zhihu['title'] = self.title
        zhihu['content'] = self.content
        zhihu['origin'] = self.origin
        zhihu['originurl'] = self.originurl
        zhihu['aurl'] = self.url
        # requests.post(url=huginnUrl,data=zhihu)
        return zhihu

    def get_zhihu_article(self):
        selector = util.get_selector(url=self.url, headers=self.headers)
        self.title = selector.xpath('string(//h1)')
        upvote = selector.xpath('string(//button[@class="Button VoteButton VoteButton--up"])')
        content = str(etree.tostring(selector.xpath('//div[contains(@class,"RichText") and contains(@class,"ztext")]')[0],
                           encoding="utf-8"), encoding='utf-8')
        self.content = upvote + '<br>' + content
        self.origin = selector.xpath('string(//a[@class="UserLink-link"])')
        self.originurl = selector.xpath('string(//a[@class="UserLink-link"]/@href)')

    def get_zhihu_answer(self):
        selector = util.get_selector(url=self.url, headers=self.headers)
        upvote = selector.xpath('string(//button[contains(@class,"VoteButton")])')
        content = str(etree.tostring(selector.xpath('//span[contains(@class,"RichText") and @itemprop="text"]')[0],encoding="utf-8"), encoding='utf-8')
        # question = str(
        #     etree.tostring(selector.xpath('//div[contains(@class,"QuestionRichText")]')[0],
        #                    encoding="utf-8"), encoding='utf-8')
        self.origin = selector.xpath('string(//div[@class="AuthorInfo"]//meta[@itemprop="name"]/@content)')
        self.originurl = selector.xpath('string(//div[@class="AuthorInfo"]//meta[@itemprop="url"]/@content)')
        if self.originurl == 'https://www.zhihu.com/people/':
            self.originurl = ''
        self.content = upvote + '<br>' + content
        self.title = selector.xpath('string(//h1)')

    def get_zhihu_status(self):
        selector = util.get_selector(url=self.url, headers=self.headers)
        content = str(etree.tostring(selector.xpath('//span[contains(@class,"RichText") and @itemprop="text"]')[0],
                                     encoding="utf-8"), encoding='utf-8')
        upvote = selector.xpath('string(//button[contains(@class,"VoteButton")]//span)')
        timestamp = selector.xpath('string(//div[@class="ContentItem-time"]//span)')
        if selector.xpath('string(//div[@class="RichContent"]/div[2]/div[2]/@class)').find('PinItem-content-originpin') != -1: #是否存在转发
            # retweet_html = selector.xpath('//div[contains(@class,"PinItem-content-originpin")]')
            # print(selector.xpath('//div[contains(@class,"PinItem-content-originpin")]/div[3]'))
            if str(etree.tostring(selector.xpath('//div[contains(@class,"PinItem-content-originpin")]/div[3]')[0],
                               encoding="utf-8"), encoding='utf-8') != '<div class="RichText ztext PinItem-remainContentRichText"/>': # 如果转发内容有图
                pichtml=html.fromstring(str(etree.tostring(selector.xpath('//div[contains(@class,"PinItem-content-originpin")]')[0],
                                   encoding="utf-8"), encoding='utf-8'))
                # for i in pichtml.iter('img'):
                #     i.attrib['src'] = 'sb'
                #     i.attrib['data-original'] = 'src'
                self.retweet_html=str(html.tostring(pichtml,pretty_print=True)).replace('b\'<div','<div')
                # self.retweet_html=str(pichtml)
                print(type(self.retweet_html))
                print(self.retweet_html)
            else:
                self.retweet_html=str(etree.tostring(selector.xpath('//div[contains(@class,"PinItem-content-originpin")]')[0],
                                                encoding="utf-8"), encoding='utf-8')
                print(self.retweet_html)
        self.content = '点赞数：' + upvote + '<br>' + content + '<br>' + self.retweet_html + '<br>' + timestamp
        self.origin = selector.xpath('string(//div[@class="AuthorInfo"]//meta[@itemprop="name"]/@content)')
        self.originurl = selector.xpath('string(//div[@class="AuthorInfo"]//meta[@itemprop="url"]/@content)')
        self.title = self.origin + '的想法'



        # if selector.xpath('//span[contains(@class,"PinItem-content-originpin")]//div[@class="Image-Wrapper-Preview"]'):
            # str(etree.tostring(selector.xpath('//span[contains(@class,"PinItem-content-originpin")]')[0],encoding="utf-8"), encoding='utf-8')




        # print(selector.xpath(''))


zhihu = Zhihu(favurl)
zhihu.get_fav_item()
