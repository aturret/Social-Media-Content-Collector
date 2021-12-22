# -*- coding:utf-8 -*-
from flask import Flask
import json
from flask import request
from html_telegraph_poster import TelegraphPoster
import requests
from collections import OrderedDict
from lxml import etree
import sys
import re

# from .verify import check

'''
flask： web框架，通过flask提供的装饰器@server.route()将普通函数转换为服务
'''


# 创建一个服务，把当前这个python文件当做一个服务
def create_app():
    server = Flask(__name__)
    list = [""]

    # server.config['JSON_AS_ASCII'] = False
    # @server.route()可以将普通函数转变为服务 登录接口的路径、请求方式
    @server.route('/weiboConvert1', methods=['get', 'post'])
    # @server.route('/telegraphConvert', methods=['get', 'post'])
    # @server.route('/tweetAPIConvert', methods=['get', 'post'])

    def weiboConvert1():
        weiboData = request.get_data()
        wdict = json.loads(weiboData)
        print(wdict['url'])
        wurl = wdict['url']
        if wurl.find('weibo.com'):
            wurl=wurl.replace('weibo.com','m.weibo.cn')
        # if re.match(pattern=r'weibo\.com', string=wurl):
        #     re.sub(pattern=r'weibo\.com', repl='m.weibo.cn', string=wurl)
        print(wurl)
        return '1'

    @server.route('/weiboConvert', methods=['get', 'post'])
    def weiboConvert():

        weiboData = request.get_data()
        wdict = json.loads(weiboData)
        print(wdict['url'])
        wurl = wdict['url']
        if wurl.find('weibo.com'):
            wurl=wurl.replace('weibo.com','m.weibo.cn')

        class Weibo(object):
            def __init__(self, url):
                self.headers = {
                    'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
                    'Cookie': ''}
                self.url = url

            def get_weibo(self):
                html = requests.get(self.url, headers=self.headers, verify=False).text
                html = html[html.find('"status":'):]
                html = html[:html.rfind('"hotScheme"')]
                html = html[:html.rfind(',')]
                html = '{' + html + '}'
                js = json.loads(html, strict=False)
                weibo_info = js.get('status')
                if weibo_info:
                    weibo = self.parse_weibo(weibo_info)
                    return weibo

            def get_article_url(self, selector):
                """获取微博中头条文章的url"""
                article_url = ''
                text = selector.xpath('string(.)')
                if text.startswith(u'发布了头条文章'):
                    url = selector.xpath('//a/@data-url')
                    if url and url[0].startswith('http://t.cn'):
                        article_url = url[0]
                return article_url

            def get_pics(self, weibo_info):
                """获取微博原始图片url"""
                if weibo_info.get('pics'):
                    pic_info = weibo_info['pics']
                    pic_list = [pic['large']['url'] for pic in pic_info]
                    pics = ','.join(pic_list)
                else:
                    pics = ''
                return pics

            def get_pics_new(self, weibo_info):
                """获取微博原始图片url"""
                if weibo_info.get('pics'):
                    pic_info = weibo_info['pics']
                    pic_list = [pic['large']['url'] for pic in pic_info]
                    pics = pic_list
                else:
                    pics = ''
                return pics

            def get_video_url(self, weibo_info):
                """获取微博视频url"""
                video_url = ''
                video_url_list = []
                if weibo_info.get('page_info'):
                    if ((weibo_info['page_info'].get('urls')
                         or weibo_info['page_info'].get('media_info'))
                            and weibo_info['page_info'].get('type') == 'video'):
                        media_info = weibo_info['page_info']['urls']
                        if not media_info:
                            media_info = weibo_info['page_info']['media_info']
                        video_url = media_info.get('mp4_720p_mp4')
                        if not video_url:
                            video_url = media_info.get('mp4_hd_url')
                        if not video_url:
                            video_url = media_info.get('hevc_mp4_hd')
                        if not video_url:
                            video_url = media_info.get('mp4_sd_url')
                        if not video_url:
                            video_url = media_info.get('mp4_ld_mp4')
                        if not video_url:
                            video_url = media_info.get('stream_url_hd')
                        if not video_url:
                            video_url = media_info.get('stream_url')
                if video_url:
                    video_url_list.append(video_url)
                live_photo_list = self.get_live_photo(weibo_info)
                if live_photo_list:
                    video_url_list += live_photo_list
                return ';'.join(video_url_list)

            def get_live_photo(self, weibo_info):
                """获取live photo中的视频url"""
                live_photo_list = []
                live_photo = weibo_info.get('pic_video')
                if live_photo:
                    prefix = 'https://video.weibo.com/media/play?livephoto=//us.sinaimg.cn/'
                    for i in live_photo.split(','):
                        if len(i.split(':')) == 2:
                            url = prefix + i.split(':')[1] + '.mov'
                            live_photo_list.append(url)
                    return live_photo_list

            def get_location(self, selector):
                """获取微博发布位置"""
                location_icon = 'timeline_card_small_location_default.png'
                span_list = selector.xpath('//span')
                location = ''
                for i, span in enumerate(span_list):
                    if span.xpath('img/@src'):
                        if location_icon in span.xpath('img/@src')[0]:
                            location = span_list[i + 1].xpath('string(.)')
                            break
                return location

            def standardize_info(self, weibo):
                for k, v in weibo.items():
                    if 'bool' not in str(type(v)) and 'int' not in str(
                            type(v)) and 'list' not in str(
                        type(v)) and 'long' not in str(type(v)):
                        weibo[k] = v.replace(u'\u200b', '').encode(
                            sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding)
                return weibo

            def string_to_int(self, string):
                """字符串转换为整数"""
                if isinstance(string, int):
                    return string
                elif string.endswith(u'万+'):
                    string = string[:-2] + '0000'
                elif string.endswith(u'万'):
                    string = float(string[:-1]) * 10000
                elif string.endswith(u'亿'):
                    string = float(string[:-1]) * 100000000
                return int(string)

            def get_topics(self, selector):
                """获取参与的微博话题"""
                span_list = selector.xpath("//span[@class='surl-text']")
                topics = ''
                topic_list = []
                for span in span_list:
                    text = span.xpath('string(.)')
                    if len(text) > 2 and text[0] == '#' and text[-1] == '#':
                        topic_list.append(text[1:-1])
                if topic_list:
                    topics = ','.join(topic_list)
                return topics

            def get_at_users(self, selector):
                """获取@用户"""
                a_list = selector.xpath('//a')
                at_users = ''
                at_list = []
                for a in a_list:
                    if '@' + a.xpath('@href')[0][3:] == a.xpath('string(.)'):
                        at_list.append(a.xpath('string(.)')[1:])
                if at_list:
                    at_users = ','.join(at_list)
                return at_users

            def parse_weibo(self, weibo_info):
                weibo = OrderedDict()
                if weibo_info['user']:
                    weibo['user_id'] = weibo_info['user']['id']
                    weibo['screen_name'] = weibo_info['user']['screen_name']
                else:
                    weibo['user_id'] = ''
                    weibo['screen_name'] = ''
                weibo['id'] = int(weibo_info['id'])
                weibo['bid'] = weibo_info['bid']
                text_body = weibo_info['text']
                selector = etree.HTML(text_body)
                # if self.remove_html_tag:
                #     weibo['text'] = selector.xpath('string(.)')
                # else:
                weibo['text'] = text_body
                weibo['article_url'] = self.get_article_url(selector)
                weibo['pics'] = self.get_pics(weibo_info)
                weibo['pics_new'] = self.get_pics_new(weibo_info)
                weibo['video_url'] = self.get_video_url(weibo_info)
                weibo['location'] = self.get_location(selector)
                weibo['created_at'] = weibo_info['created_at']
                weibo['source'] = weibo_info['source']
                weibo['attitudes_count'] = self.string_to_int(
                    weibo_info.get('attitudes_count', 0))
                weibo['comments_count'] = self.string_to_int(
                    weibo_info.get('comments_count', 0))
                weibo['reposts_count'] = self.string_to_int(
                    weibo_info.get('reposts_count', 0))
                weibo['topics'] = self.get_topics(selector)
                weibo['at_users'] = self.get_at_users(selector)
                # piclist = json.loads(weibo['pics_new'])
                picsformat = ''
                videoformat = ''
                if weibo['pics_new'] != '':
                    piclist = weibo['pics_new']
                    for i in piclist:
                        picsformat += '<img src="' + i + '"><br />'
                        print(picsformat)
                if weibo['video_url'] != '':
                    videoformat = '<video><source src="' + weibo['video_url'] + '" type="video/mp4">youcannotwatchthevideo</video>'
                weibo['content'] = weibo['text'] + '<br />' + picsformat + videoformat
                weibo['title'] = weibo['screen_name'] + '的微博'
                weibo['origin'] = weibo['screen_name']
                weibo['aurl'] = 'https://weibo.com/u/' + str(weibo['user_id'])
                weibo['originurl'] = self.url
                return self.standardize_info(weibo)

        huginnUrl='https://huginn.aturret.top/users/2/web_requests/56/shelleysmummydied'
        wb = Weibo(wurl)
        print(wb.get_weibo())
        requests.post(url=huginnUrl,data=wb.get_weibo())
        return wb.get_weibo()

    # def tweetAPIConvert():
    #     # receivedUrl = request.get_data()
    #     # dict = json.loads(broadcastData)
    @server.route('/telegraphConvert', methods=['get', 'post'])
    def telegraphConvert():
        author = 'origin'
        author_url = 'originurl'
        article_url = 'aurl'
        title = 'title'
        content = 'content'
        # huginn webhook
        url = 'https://huginn.aturret.top/users/2/web_requests/21/supersbshelley'

        broadcastData = request.get_data()
        dict = json.loads(broadcastData)
        print(dict[title])

        def post():
            t = TelegraphPoster(use_api=True)
            short_name = dict[author]

            t.create_api_token(short_name[0:14], dict[author], dict[article_url])

            a = t.post(dict[title], dict[author], dict[content])
            print(a['url'])
            b = {'url': ''}
            b['url'] = a['url']
            r = requests.post(url, data=b)
            print(r.text)

        print(list)
        # 检测标题是否重复
        i = 0
        while 1 == 1:
            if dict[title] != list[i]:
                i = i + 1
                if i == len(list):
                    list.append(dict[title])
                    print(list)
                    post()

                    break
            else:
                print("same one")
                break

        # a=t.post(dict[title], dict[author],dict[content])
        # print (a['url'])
        # b={'url':''}
        # b['url']=a['url']
        # r=requests.post(url,data=b)
        # print(r.text)
        # # # url =

        return ('mission accomplished')

    return server
