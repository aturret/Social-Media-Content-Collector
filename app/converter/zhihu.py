# -*- coding: UTF-8 -*-
import requests
import time  # import cchardet as chardet
from collections import OrderedDict
from app.utils import util
from bs4 import BeautifulSoup

import re

# import util
from html_sanitizer import Sanitizer

favurl = 'https://www.zhihu.com/pin/1457225488036573184'
zhihu_host = 'https://www.zhihu.com'
zhihu_api_host = 'https://www.zhihu.com/api/v4'
zhihu_columns_api_host = 'https://zhuanlan.zhihu.com/api'
zhihu_type_translate = {
    'article': '专栏文章',
    'answer': '回答',
    'status': '想法'
}

# huginnUrl = 'https://huginn.aturret.top/users/2/web_requests/67/shelleyisanoobplayer'


class Zhihu(object):

    def __init__(self, favurl='', url='', **kwargs):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Cookie': '',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        self.method = kwargs.get('method', 'api')
        self.zhihu_type = ''
        self.api_url = ''
        self.url = url
        self.aurl = ''
        self.content = ''
        self.text = ''
        self.author = ''
        self.author_url = ''
        self.title = ''
        self.favurl = favurl
        self.question = ''
        self.workurl = ''
        self.groupname = ''
        self.groupurl = ''
        self.retweet_html = ''
        self.type = 'long'
        self.media_files = []
        self.created = '',
        self.updated = ''

    def to_dict(self):
        zhihu_dict = {}
        for key in self.__dict__:
            if key == 'headers':
                continue
            zhihu_dict[key] = self.__dict__[key]
        return zhihu_dict

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
        if util.get_html_text_length(self.content) < 200:
            self.type = 'short'
        result = self.to_dict()
        return result

    def get_zhihu_article(self):
        self.zhihu_type = 'article'
        if self.method == 'api':
            self.api_url = zhihu_columns_api_host + '/articles/' + re.findall(r'/p/(\d+)\D*', self.url)[0]
            json_data = util.get_response_json(self.api_url, headers=self.headers)
            self.title = json_data['title']
            self.content = json_data['content']
            self.author = json_data['author']['name']
            self.author_url = zhihu_host + '/people/' + json_data['author']['url_token']
            upvote = json_data['voteup_count']
            self.get_zhihu_short_text()
        elif self.method == 'html':
            self.zhihu_type = 'article'
            selector = util.get_selector(url=self.url, headers=self.headers)
            self.title = selector.xpath('string(//h1)')
            upvote = selector.xpath('string(//button[@class="Button VoteButton VoteButton--up"])')
            self.content = str(
                util.etree.tostring(selector.xpath('//div[contains(@class,"RichText") and contains(@class,"ztext")]')[0],
                               encoding="utf-8"), encoding='utf-8')
            self.get_zhihu_short_text()
            self.content = upvote + '<br>' + self.content
            self.author = selector.xpath('string(//div[contains(@class,"AuthorInfo-head")]//a)')
            self.author_url = 'https:' + selector.xpath('string(//a[@class="UserLink-link"]/@href)')

    def get_zhihu_answer(self):
        self.zhihu_type = 'answer'
        selector = util.get_selector(url=self.url, headers=self.headers)
        upvote = selector.xpath('string(//button[contains(@class,"VoteButton")])')
        self.content = str(util.etree.tostring(selector.xpath(
            '//div[contains(@class,"RichContent-inner")]//span[contains(@class,"RichText") and @itemprop="text"]')[0],
                                     encoding="utf-8"), encoding='utf-8')
        self.title = selector.xpath('string(//h1)')
        self.author = selector.xpath('string(//div[@class="AuthorInfo"]//meta[@itemprop="name"]/@content)')
        self.author_url = selector.xpath('string(//div[@class="AuthorInfo"]//meta[@itemprop="url"]/@content)')
        self.get_zhihu_short_text()
        if self.author_url == 'https://www.zhihu.com/people/':
            self.author_url = ''
        self.content = '<p>' + upvote + '</p><br>' + self.content

    def get_zhihu_status(self):
        self.zhihu_type = 'status'
        if self.method == 'api':
            self.api_url = 'https://www.zhihu.com/api/v4/pins/' + re.findall(r'pin/(\d+)\D*', self.url)[0]
            print(self.api_url)
            # json_data = get_response_json(self.url, headers=self.headers, test=True)
            json_data = get_zhihu_json_data(self.api_url, headers=self.headers)
            self.author = json_data['author']['name']
            self.author_url = zhihu_host + '/people/' + json_data['author']['url_token']
            self.title = self.author + '的想法'
            self.content = json_data['content_html']
            self.get_zhihu_short_text()
            self.created = util.unix_timestamp_to_utc(json_data['created'])
            self.updated = util.unix_timestamp_to_utc(json_data['updated'])
            timestamp = '修改于：' + self.updated if json_data['updated'] > json_data['created'] \
                else '发布于：' + self.created
            upvote = json_data['like_count']
            self.content = '点赞数：' + str(upvote) + '<br>' + self.content + '<br>' + self.retweet_html + '<br>' + timestamp
        elif self.method == 'html':
            selector = util.get_selector(url=self.url, headers=self.headers)
            content = str(util.etree.tostring(selector.xpath('//span[contains(@class,"RichText") and @itemprop="text"]')[0],
                                         encoding="utf-8"), encoding='utf-8')
            upvote = selector.xpath('string(//button[contains(@class,"VoteButton")]//span)')
            timestamp = selector.xpath('string(//div[@class="ContentItem-time"]//span)')
            if selector.xpath('string(//div[@class="RichContent"]/div[2]/div[2]/@class)').find(
                    'PinItem-content-originpin') != -1:  # 是否存在转发
                if str(util.etree.tostring(selector.xpath('//div[contains(@class,"PinItem-content-originpin")]/div[3]')[0],
                                      encoding="utf-8"),
                       encoding='utf-8') != '<div class="RichText ztext PinItem-remainContentRichText"/>':  # 如果转发内容有图
                    pichtml = util.lhtml.fromstring(
                        str(util.etree.tostring(selector.xpath('//div[contains(@class,"PinItem-content-originpin")]')[0],
                                           encoding="utf-8"), encoding='utf-8'))
                    self.retweet_html = str(util.lhtml.tostring(pichtml, pretty_print=True)).replace('b\'<div', '<div')
                    print(type(self.retweet_html))
                    print(self.retweet_html)
                else:
                    self.retweet_html = str(
                        util.etree.tostring(selector.xpath('//div[contains(@class,"PinItem-content-originpin")]')[0],
                                       encoding="utf-8"), encoding='utf-8')
                    print(self.retweet_html)
            self.content = '点赞数：' + upvote + '<br>' + content + '<br>' + self.retweet_html + '<br>' + timestamp
            self.author = selector.xpath('string(//div[@class="AuthorInfo"]//meta[@itemprop="name"]/@content)')
            self.author_url = selector.xpath('string(//div[@class="AuthorInfo"]//meta[@itemprop="url"]/@content)')
            self.title = self.author + '的想法'

    def get_zhihu_short_text(self):
        soup = BeautifulSoup(self.content, 'html.parser')
        for img in soup.find_all('img'):
            if img['src'].find('data:image') != -1:
                continue
            media_item = {'type': 'image', 'url': img['src'], 'caption': ''}
            self.media_files.append(media_item)
            img.decompose()
        for figure in soup.find_all('figure'):
            figure.append(BeautifulSoup('<br>', 'html.parser'))
            figure.decompose()
        print(self.content)
        if self.zhihu_type == 'status':
            self.text = '<a href="' + self.aurl + '"><b>' + self.title + '</b>' + \
                        '</a>：' + str(soup)
        else:
            self.text = '<a href="' + self.aurl + '"><b>' + self.title + '</b> - ' + self.author + '的' + \
                        zhihu_type_translate[self.zhihu_type] + '</a>：\n' + str(soup)
        soup = BeautifulSoup(self.text, 'html.parser')
        soup = util.format_telegram_short_text(soup)
        for p in soup.find_all('p'):
            if p.text != '':
                p.append(BeautifulSoup('<br>', 'html.parser'))
            p.unwrap()
        self.text = str(soup).replace('<br/>', '\n').replace('<br>', '\n').replace('<br />', '').replace('<hr/>', '\n')


def get_zhihu_json_data(url, headers):
    soup = BeautifulSoup(util.get_response(url).text, 'html.parser')
    print(soup.text)
    # json_data = json.loads(soup.find('script', attrs={'id': 'js-initialData'}).text)
    json_data = util.json.loads(soup.text)
    return json_data
