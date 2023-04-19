# -*- coding:utf-8 -*-
from flask import Flask
import json
from flask import request
from html_telegraph_poster import TelegraphPoster
from html_telegraph_poster.utils import DocumentPreprocessor
import threading
import traceback
from . import atelebot_async, atelebot, combination, settings
from .utils import telegraph, util
from .converter import zhihu, twitter, douban, weibo
import time
import asyncio


# from time import sleep
# import toml


# from .verify import check


def create_app():
    server = Flask(__name__)
    c_title = ""
    c_list = [""]
    site_url = 'http://' + settings.env_var.get('SITE_URL', '127.0.0.1:' + settings.env_var.get('PORT', '1045'))
    print(site_url)
    print(settings.env_var.get('PORT', 'no port'))
    telegraph_url = site_url + '/telegraphConvert'

    @server.route('/newWeiboConvert', methods=['get', 'post'])
    def newWeiboConvert():
        try:
            weiboData = request.get_data()
            wdict = json.loads(weiboData)
            print(wdict['url'])
            wurl = wdict['url']
            if wurl.find('weibo.com'):
                wurl = wurl.replace('weibo.com', 'm.weibo.cn')
            wb = weibo.Weibo(wurl).new_get_weibo()
            if not wb:
                raise Exception('No weibo found')
            print(wb)
            temp_html = DocumentPreprocessor(wb['content'])
            temp_html.upload_all_images()
            wb['content'] = temp_html.get_processed_html()
            tdict = {
                'content': wb['content'],
                'title': wb['title'],
                'origin': wb['origin'],
                'originurl': wb['originurl'],
                'url': wb['aurl']
            }
            print(tdict)
            # t_url = requests.post(url=telegraph_url, json=tdict).text
            t_url = util.telegraph_convert(tdict)
            print(t_url)
            mdict = {
                'category': 'weibo',
                'title': wb['title'],
                'origin': wb['origin'],
                'aurl': wb['aurl'],
                'originurl': wb['originurl'],
                'text': wb['text'],
                'message': '',
                'turl': t_url,
                'type': wb['type'] if 'type' in wb else 'long',
                'media_files': wb['media_files'] if 'media_files' in wb else []
            }
            print(mdict)
        except Exception:
            print(traceback.format_exc())
            return False
        return mdict

    @server.route('/weiboConvert', methods=['get', 'post'])
    def weibo_convert():
        try:
            weiboData = request.get_data()
            wdict = json.loads(weiboData)
            print(wdict['url'])
            wurl = wdict['url']
            if wurl.find('weibo.com'):
                wurl = wurl.replace('weibo.com', 'm.weibo.cn')
            wb = weibo.Weibo(wurl).get_weibo()
            print(wb)
            temp_html = DocumentPreprocessor(wb['content'])
            temp_html.upload_all_images()
            wb['content'] = temp_html.get_processed_html()
            tdict = {
                'content': wb['content'],
                'title': wb['title'],
                'origin': wb['origin'],
                'originurl': wb['originurl'],
                'url': wb['aurl'],
                'type': wb['type'] if 'type' in wb else 'long'
            }
            print(tdict)
            # t_url = requests.post(url=telegraph_url, json=tdict).text
            t_url = util.telegraph_convert(tdict)
            print(t_url)
            mdict = {
                'category': 'weibo',
                'title': wb['title'],
                'origin': wb['origin'],
                'aurl': wb['aurl'],
                'originurl': wb['originurl'],
                'message': '',
                'turl': t_url
            }
            print(mdict)
        except Exception:
            print(traceback.format_exc())
            return False
        return mdict

    @server.route('/doubanConvert', methods=['get', 'post'])
    def douban_convert():
        try:
            doubanData = request.get_data()
            ddict = json.loads(doubanData)
            print(ddict['url'])
            douban_url = ddict['url']
            data_dict = douban.Douban(url=douban_url).get_fav_item()
            tdict = {
                'content': data_dict['content'],
                'title': data_dict['title'],
                'origin': data_dict['origin'],
                'originurl': data_dict['originurl'],
                'url': data_dict['aurl'],
            }
            print(tdict)
            # t_url = requests.post(url=telegraph_url, json=tdict).text
            t_url = util.telegraph_convert(tdict)
            mdict = {
                'category': 'Douban',
                'title': data_dict['title'],
                'origin': data_dict['origin'],
                'aurl': data_dict['aurl'],
                'originurl': data_dict['originurl'],
                'message': '',
                'turl': t_url,
                'type': data_dict['type'] if 'type' in data_dict else 'long'
            }
            print(mdict)
            # atelebot.send_to_channel(data=mdict)
        except Exception:
            print(traceback.format_exc())
            return 'Failed'
        return mdict
        # db = douban.Douban(url=durl,huginnUrl=huginnUrl)
        # db.get_fav_item(url=db.url)
        # return db.get_fav_item()

    @server.route('/twitterConvert', methods=['get', 'post'])
    def twitter_convert():
        try:
            twitter_data = request.get_data()  # 获取推文链接
            response_dict = json.loads(twitter_data)
            print(response_dict['url'])
            twitter_url = response_dict['url']
            data_dict = twitter.Twitter(url=twitter_url).get_single_tweet()
            tdict = {
                'content': data_dict['content'],
                'title': data_dict['title'],
                'origin': data_dict['origin'],
                'originurl': data_dict['originurl'],
                'url': data_dict['aurl']
            }
            print(tdict)
            t_url = util.telegraph_convert(tdict)
            mdict = {
                'category': 'twitter',
                'title': data_dict['title'],
                'origin': data_dict['origin'],
                'aurl': data_dict['aurl'],
                'originurl': data_dict['originurl'],
                'message': '',
                'turl': t_url,
                'type': data_dict['type'] if 'type' in data_dict else 'long'
            }
            print(mdict)
        except Exception:
            print(traceback.format_exc())
            return 'Failed'
        return mdict

    @server.route('/zhihuConvert', methods=['get', 'post'])
    def zhihu_convert():
        try:
            zhihu_data = request.get_data()
            zdict = json.loads(zhihu_data)
            print(zdict['url'])
            zhihu_url = zdict['url']
            t_url = 'nothing'
            data_dict = zhihu.Zhihu(url=zhihu_url).get_fav_item()
            tdict = {
                'content': data_dict['content'],
                'title': data_dict['title'],
                'origin': data_dict['origin'],
                'originurl': data_dict['originurl'],
                'url': data_dict['aurl']
            }
            print(tdict)
            # t_url = requests.post(url=telegraph_url, json=tdict).text
            failure_counter = 0

            while failure_counter < 5:
                try:
                    t_url = util.telegraph_convert(tdict)
                    if t_url != 'nothing':
                        break
                except Exception:
                    failure_counter += 1
                    print(traceback.format_exc())
                    continue
            mdict = {
                'category': 'Zhihu',
                'title': data_dict['title'],
                'origin': data_dict['origin'],
                'aurl': data_dict['aurl'],
                'originurl': data_dict['originurl'],
                'message': '',
                'turl': t_url,
                'type': data_dict['type'] if 'type' in data_dict else 'long'
            }
            print(mdict)
        except Exception:
            print(traceback.format_exc())
            return 'Failed'
        return mdict

    @server.route('/inoreaderConvert', methods=['get', 'post'])
    def inoreader_convert():
        try:
            inoreader_data = request.get_data()
            t_url = 'nothing'
            data_dict = json.loads(inoreader_data)
            print(data_dict)
            tdict = {
                'content': data_dict['content'],
                'title': data_dict['title'],
                'origin': data_dict['origin'],
                'originurl': data_dict['originurl'],
                'url': data_dict['aurl']
            }
            print(tdict)
            # t_url = requests.post(url=telegraph_url, json=tdict).text
            a = 0
            while a < 5:
                try:
                    t_url = util.telegraph_convert(tdict)
                    print(t_url)
                    if t_url != 'nothing':
                        break
                except Exception:
                    time.sleep(1)
                    a += 1
                    print(traceback.format_exc())
                    continue
            mdict = {
                'category': data_dict['tag'],
                'title': data_dict['title'],
                'origin': data_dict['origin'],
                'aurl': data_dict['aurl'],
                'originurl': data_dict['originurl'],
                'message': data_dict['message'] + '\n' if data_dict['message'] else '',
                'turl': t_url,
                'type': data_dict['type'] if 'type' in data_dict else 'long'
            }
            print(mdict)
            atelebot.send_to_channel(data=mdict)
        except Exception:
            print(traceback.format_exc())
            return 'Failed'
        return mdict

    @server.route('/telegraphConvert', methods=['get', 'post'])
    def telegraph_convert(check=True):
        res = ''
        # url = 'https://'+cfg['huginn']['url']+'/users/2/web_requests/'+cfg['huginn']['webrequest']['telegraph']
        # definite the keys of the json file
        author = 'origin'
        author_url = 'originurl'
        title = 'title'
        content = 'content'
        content_data = request.get_data()
        print(content_data)
        metadata_dict = json.loads(content_data)
        # metadata_dict = content_data
        print(type(metadata_dict))
        print(metadata_dict)

        # Use pyhtmltotelegraph to post telegraph article
        def post():
            try:
                t = TelegraphPoster(use_api=True)
                short_name = metadata_dict[author]
                t.create_api_token(short_name[0:14], author_name=metadata_dict[author])
                telegraphPost = t.post(title=metadata_dict['title'], author=metadata_dict[author],
                                       text=metadata_dict['content'], author_url=metadata_dict[author_url])
                print(telegraphPost['url'])
                print(type(telegraphPost))
                telegraphPostJSON = {'url': ''}
                telegraphPostJSON['url'] = telegraphPost['url']
                # r = requests.post(url=url, data=telegraphPostJSON)
                # print(r.text)
                return telegraphPost['url']
            except Exception:
                print(traceback.format_exc())

        print(c_list)
        # check if the title is a duplicate
        if check:
            if c_list[0] != title:
                res = post()
                c_list.pop()
                c_list.append(title)
            else:
                print("same one")
        else:
            res = post()
        return res if res else 'nothing'

    # if settings.env_var.get('BOT', 'True') == 'True':
    telebot_thread = threading.Thread(target=atelebot.bot.polling, daemon=True)
    telebot_thread.start()  # start the bot in a thread instead

    return server
