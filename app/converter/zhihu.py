# -*- coding: UTF-8 -*-
import requests
import time
# import cchardet as chardet
from bs4 import BeautifulSoup
from lxml import etree, html
from collections import OrderedDict
from app.utils import util

import re

# import util
from html_sanitizer import Sanitizer

favurl = 'https://www.zhihu.com/pin/1457225488036573184'

# huginnUrl = 'https://huginn.aturret.top/users/2/web_requests/67/shelleyisanoobplayer'


class Zhihu(object):
    def __init__(self, favurl='',url=''):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Cookie': '',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        self.url = url
        self.aurl = ''
        self.content = ''
        self.text = ''
        self.origin = ''
        self.originurl = ''
        self.title = ''
        self.favurl = favurl
        self.question = ''
        self.workurl = ''
        self.groupname = ''
        self.groupurl = ''
        self.retweet_html = ''
        self.type = 'long'
        self.media_files = []

    def to_dict(self):
        return {
            'url': self.url,
            'aurl': self.aurl,
            'content': self.content,
            'text': self.text,
            'origin': self.origin,
            'originurl': self.originurl,
            'title': self.title,
            'favurl': self.favurl,
            'question': self.question,
            'workurl': self.workurl,
            'groupname': self.groupname,
            'groupurl': self.groupurl,
            'retweet_html': self.retweet_html,
            'type': self.type,
            'media_files': self.media_files
        }

    def get_fav_item(self):
        url = self.url
        self.aurl = url
        if url.find('zhuanlan.zhihu.com') != -1:
            print('检测到知乎专栏，摘取中')
            self.get_zhihu_article()
        elif url.find('answer') != -1:
            print('检测到知乎回答，摘取中')
            self.get_zhihu_answer()
        elif url.find('zhihu.com/pin/') != -1:
            print('检测到知乎想法，摘取中')
            self.get_zhihu_status()
        if len(html.fromstring(self.content).xpath('string()')) < 200:
            self.type = 'short'
        soup = BeautifulSoup(self.content, 'html.parser')
        for img in soup.find_all('img'):
            if img['src'].find('data:image') != -1:
                continue
            media_item = {'type': 'image', 'url': img['src'], 'caption': ''}
            self.media_files.append(media_item)
        for figure in soup.find_all('figure'):
            figure.decompose()
        print(self.content)
        self.text = '<a href="' + self.aurl + '"><b>' + self.title + '</b> - ' + self.origin + '的回答</a>：' + \
                    str(soup)
        soup = BeautifulSoup(self.text, 'html.parser')
        for span in soup.find_all('span'):
            span.unwrap()
        for br in soup.find_all('br'):
            br.decompose()
        for p in soup.find_all('p'):
            if p.text != '':
                p.append(BeautifulSoup('<br>', 'html.parser'))
            p.unwrap()
        self.text = str(soup).replace('<br/>', '\n').replace('<br>', '\n').replace('<br />', '')
        zhihu = self.to_dict()
        return zhihu

    def get_zhihu_article(self):
        selector = util.get_selector(url=self.url, headers=self.headers)
        self.title = selector.xpath('string(//h1)')
        upvote = selector.xpath('string(//button[@class="Button VoteButton VoteButton--up"])')
        content = str(etree.tostring(selector.xpath('//div[contains(@class,"RichText") and contains(@class,"ztext")]')[0],
                           encoding="utf-8"), encoding='utf-8')
        self.content = upvote + '<br>' + content
        self.origin = selector.xpath('string(//div[contains(@class,"AuthorInfo-head")]//a)')
        self.originurl = 'https:'+selector.xpath('string(//a[@class="UserLink-link"]/@href)')

    def get_zhihu_answer(self):
        selector = util.get_selector(url=self.url, headers=self.headers)
        upvote = selector.xpath('string(//button[contains(@class,"VoteButton")])')
        content = str(etree.tostring(selector.xpath('//div[contains(@class,"RichContent-inner")]//span[contains(@class,"RichText") and @itemprop="text"]')[0],encoding="utf-8"), encoding='utf-8')
        # question = str(
        #     etree.tostring(selector.xpath('//div[contains(@class,"QuestionRichText")]')[0],
        #                    encoding="utf-8"), encoding='utf-8')
        self.origin = selector.xpath('string(//div[@class="AuthorInfo"]//meta[@itemprop="name"]/@content)')
        self.originurl = selector.xpath('string(//div[@class="AuthorInfo"]//meta[@itemprop="url"]/@content)')
        if self.originurl == 'https://www.zhihu.com/people/':
            self.originurl = ''
        self.content = '<p>' + upvote + '</p><br>' + content
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

## TEST CODE ###
# url = 'https://www.zhihu.com/question/20953633/answer/196306254'
# zhihu = Zhihu(url=url,favurl=favurl)
# zhihu.get_fav_item()
