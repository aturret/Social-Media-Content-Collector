# -*- coding: UTF-8 -*-
import traceback
from collections import OrderedDict
from bs4 import BeautifulSoup
import re
from app.utils import util
from app import settings

# import utils

myfavlist = 'https://www.douban.com/doulist/145693559/'
testurl = 'https://m.weibo.cn/status/4717569200881723'
default_scraper = settings.env_var.get('SCRAPER', 'requests')


class Douban(object):
    def __init__(self, favurl='', url='', headers=None, cookies='', scraper=default_scraper):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Cookie': cookies,
            'Accept': '*/*',
            'Connection': 'keep-alive'
        } if headers is None else headers
        self.url = url
        self.aurl = ''
        self.text = ''
        self.content = ''
        self.author = ''
        self.author_url = ''
        self.title = ''
        self.comment = ''
        self.fav_url = favurl
        self.work_title = ''
        self.work_url = ''
        self.group_name = ''
        self.group_url = ''
        self.scraper = scraper
        self.type = 'long'
        self.media_files = []

    def to_dict(self):
        return {
            'url': self.url,
            'aurl': self.aurl,
            'text': self.text,
            'content': self.content,
            'author': self.author,
            'author_url': self.author_url,
            'title': self.title,
            'comment': self.comment,
            'fav_url': self.fav_url,
            'work_title': self.work_title,
            'work_url': self.work_url,
            'group_name': self.group_name,
            'group_url': self.group_url,
            'type': self.type,
            'media_files': self.media_files,
            'scraper': self.scraper
        }

    def get_fav_list(self):
        selector = util.get_selector(url=self.fav_url, headers=self.headers)
        print(util.local_time())
        print('豆瓣收藏夹抓取：抓取前aurl属性为：' + self.url)
        aurl = selector.xpath('string(//*[@class="doulist-item"][1]/div[1]/div[2]//a[1]/@href)')
        self.url = selector.xpath('string(//*[@class="doulist-item"][1]/div[1]/div[2]//a[1]/@href)')
        print('豆瓣收藏夹抓取：抓取出的aurl是：' + aurl)
        if aurl == self.url:  # 如果重复就不干了
            print('豆瓣收藏夹抓取：与上一次抓取的url相同，弹出')
            return '1'
        else:
            if selector.xpath('//*[@class="doulist-item"][1]//div[@class="ft"]/text()')[0].find('评语') != -1:
                print('检测到评语，抓取评语')
                comment = re.search(pattern='(?<=(评语：)).[^(\n)]*', string=selector.xpath(
                    'string(//*[@class="doulist-item"][1]//blockquote[@class="comment"])')).group()
                print('评语为：' + comment)
            else:
                comment = ''
                print('没有评语')
            # aurl = 'https://www.douban.com/people/54793495/status/3702215426/?_i=0615039ZD7VEW1'  # 测试语句
            self.get_fav_item(url=aurl, comment=comment)
            return '1'

    def get_fav_item(self, comment=''):
        url = self.url
        self.aurl = url
        douban = OrderedDict()
        douban['aurl'] = url
        douban['comment'] = comment
        try:
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
        except Exception:
            print(traceback.format_exc())
        self.douban_short_text_process()
        if util.get_html_text_length(self.text) < 200:
            self.type = 'short'
        douban['title'] = self.title
        douban['content'] = self.content
        douban['author'] = self.author
        douban['author_url'] = self.author_url
        douban['type'] = self.type
        douban['media_files'] = self.media_files
        douban['text'] = self.text
        print(self.content)
        print(self.__dict__)
        return douban

    def get_douban_note(self, url):
        if self.scraper == 'Selenium':
            selector = util.get_page_by_selenium(url, headers=self.headers)
        else:
            selector = util.get_selector(url, headers=self.headers)
            self.title = selector.xpath('string(//div[@id="content"]//h1)')
            self.content = str(util.etree.tostring(selector.xpath('//div[@id="link-report"]')[0], encoding="utf-8"),
                               encoding='utf-8')
            self.author = selector.xpath('string(//div[@class="content"]/a)')
            self.author_url = selector.xpath('string(//div[@class="content"]/a/@href)')

    def get_douban_book_review(self, url):
        selector = util.get_selector(url, headers=self.headers)
        self.title = selector.xpath('string(//div[@id="content"]//h1//span)')
        self.content = str(util.etree.tostring(selector.xpath('//div[@id="link-report"]')[0], encoding="utf-8"),
                           encoding='utf-8')
        self.author = selector.xpath('string(//header[@class="main-hd"]//span)')
        self.author_url = selector.xpath('string(//header[@class="main-hd"]/a/@href)')
        self.work_title = selector.xpath('string(//header[@class="main-hd"]/a[2])')
        self.work_url = selector.xpath('string(//header[@class="main-hd"]/a[2]/@href)')

    def get_douban_movie_review(self, url):
        selector = util.get_selector(url, headers=self.headers)
        self.title = selector.xpath('string(//div[@id="content"]//h1//span)')
        self.content = str(
            util.etree.tostring(selector.xpath('//div[contains(@class,\'review-content\')]')[0], encoding="utf-8"),
            encoding='utf-8')
        self.author = selector.xpath('string(//header[@class="main-hd"]//span)')
        self.author_url = selector.xpath('string(//header[@class="main-hd"]/a/@href)')
        self.work_title = selector.xpath('string(//header[@class="main-hd"]/a[2])')
        self.work_url = selector.xpath('string(//header[@class="main-hd"]/a[2]/@href)')

    def get_douban_status(self, url):
        selector = util.get_selector(url, headers=self.headers)
        self.content = str(util.etree.tostring(selector.xpath('//div[@class="status-saying"]')[0], encoding="utf-8"),
                           encoding='utf-8').replace('<blockquote>', '').replace('</blockquote>', '').replace('>+<',
                                                                                                              '><').replace(
            '&#13;', '<br>')
        self.author = selector.xpath('string(//div[@class="content"]/a)')
        self.author_url = selector.xpath('string(//div[@class="content"]/a/@href)')
        self.title = self.author + '的广播'

    def get_douban_group_article(self, url):
        selector = util.get_selector(url, headers=self.headers)
        self.title = selector.xpath('string(//div[@id="content"]//h1)')
        self.title = self.title.replace('\n', '').strip()
        self.content = str(util.etree.tostring(selector.xpath('//div[@id="link-report"]')[0], encoding="utf-8"),
                           encoding='utf-8')
        self.author = selector.xpath('string(//span[@class="from"]//a)')
        self.author_url = selector.xpath('string(//span[@class="from"]//a/@href)')
        self.group_name = selector.xpath('string(//div[@id="g-side-info"]//div[@class="title"]/a)')
        self.group_url = selector.xpath('string(//div[@id="g-side-info"]//div[@class="title"]/a/@href)')

    def douban_short_text_process(self):
        # TODO: customize the process of short text for each douban type.
        soup = BeautifulSoup(self.content, 'html.parser')
        self.media_files = []
        for img in soup.find_all('img'):
            media_item = {'type': 'image', 'url': img['src'], 'caption': ''}
            self.media_files.append(media_item)
            img.extract()
        for p in soup.find_all('p'):
            p.unwrap()
        for span in soup.find_all('span'):
            span.unwrap()
        for div in soup.find_all('div'):
            div.unwrap()
        for link in soup.find_all('link'):
            link.decompose()
        for script in soup.find_all('script'):
            script.decompose()
        self.text = str(soup)
        while '\n\n' in self.text:
            self.text = self.text.replace('\n\n', '\n')
        self.text = self.text.replace('<br/>', '\n').replace('<br>', '\n').replace('<br />', '\n')
        self.text = '<a href="' + self.aurl + '">' + self.author + '</a>: ' + self.text

# douban = Douban(favurl=myfavlist)
# douban.get_fav_list()

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
