# -*- coding:utf-8 -*-
from flask import Flask
import json
from flask import request
from html_telegraph_poster import TelegraphPoster
import requests
import re
import threading
from . import atelebot, weibo, douban, zhihu, telegraph, combination, util,settings
from collections import OrderedDict
import traceback
from time import sleep
import toml


# from .verify import check


def create_app():
    server = Flask(__name__)
    c_title = ""
    c_list = [""]
    site_url = 'http://'+settings.env_var.get('SITE_URL', '127.0.0.1:' + settings.env_var.get('PORT', '1045'))
    print(site_url)
    print(settings.env_var.get('PORT','no port'))
    telegraph_url = site_url+'/telegraphConvert'
    @server.route('/weiboConvert1', methods=['get', 'post'])
    def weiboConvert1():
        weiboData = request.get_data()
        wdict = json.loads(weiboData)
        print(wdict['url'])
        wurl = wdict['url']
        if wurl.find('weibo.com'):
            wurl=wurl.replace('weibo.com','m.weibo.cn')
        print(wurl)
        wb = weibo.Weibo(wurl)
        print(wb.get_weibo())
        return wb.get_weibo()

    @server.route('/weiboConvert', methods=['get', 'post'])
    def weiboConvert():
        try:
        # huginnUrl='https://'+cfg['huginn']['url']+'/users/2/web_requests/'+cfg['huginn']['webrequest']['weibo']
            weiboData = request.get_data()
            wdict = json.loads(weiboData)
            print(wdict['url'])
            wurl = wdict['url']
            if wurl.find('weibo.com'):
                wurl=wurl.replace('weibo.com','m.weibo.cn')
            wb = weibo.Weibo(wurl).get_weibo()
            print(wb)
            tdict = {
                'content': wb['content'],
                'title': wb['title'],
                'origin': wb['origin'],
                'originurl': wb['originurl'],
                'url': wb['aurl']
            }
            print(tdict)
            # t_url = requests.post(url=telegraph_url, json=tdict).text
            t_url = util.telegraphConvert(tdict)
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
        # print(wb.get_weibo())
        # requests.post(url=huginnUrl,data=wb.get_weibo())
        return mdict

    @server.route('/doubanConvert', methods=['get', 'post'])
    def doubanConvert():
        # huginnUrl = 'https://'+cfg['huginn']['url']+'/users/2/web_requests/'+cfg['huginn']['webrequest']['douban']
        doubanData = request.get_data()
        ddict = json.loads(doubanData)
        print(ddict['url'])
        durl = ddict['url']
        # db = douban.Douban(url=durl,huginnUrl=huginnUrl)
        # db.get_fav_item(url=db.url)
        # return db.get_fav_item()

    @server.route('/twitterConvert', methods=['get', 'post'])
    def twitterConvert():
        # huginnUrl = 'https://'+cfg['huginn']['url']+'/users/2/web_requests/'+cfg['huginn']['webrequest']['twitter']
        headers = {
            'Authorization' : 'Bearer '+settings.env_var.get('TWITTER_APP_KEY'),
            'Cookie' : '',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
        }
        params={
            'expansions' : 'referenced_tweets.id,referenced_tweets.id.author_id,attachments.media_keys',
            'tweet.fields' : 'created_at',
            'media.fields' : 'duration_ms,height,media_key,preview_image_url,public_metrics,type,url,width,alt_text'
        }

        twitterData = request.get_data() #获取推文链接
        tdict = json.loads(twitterData)
        print(tdict['url'])
        turl = tdict['url']
        print(turl)
        tpattern=re.compile(r'(?<=status/)[0-9]*') #摘出推文id
        tid=tpattern.search(turl).group()
        tapiurl='https://api.twitter.com/2/tweets/' + tid
        reqs = requests.get(url=tapiurl,headers=headers,params=params).json()
        # 编辑推送信息
        twitter = OrderedDict()
        twitter['text']=reqs['data']['text']
        twitter['origin']=reqs['includes']['users'][0]['name']
        twitter['title']=twitter['origin']+'\'s tweet'
        twitter['originurl']='https://twitter.com/'+ reqs['includes']['users'][0]['username']
        twitter['aurl']=turl
        picformat = '' # 处理图片
        if 'attachments' in reqs['data']:
            for i in reqs['includes']['media']:
                picformat += '<img src="' + i['url'] + '">' + '<br>'
            print(picformat)
        twitter['content']=twitter['text']+'<br>'+picformat
        print(twitter)
        # requests.post(url=huginnUrl,data=twitter)
        return reqs

    @server.route('/zhihuConvert', methods=['get', 'post'])
    def zhihuConvert():
        # huginnUrl='https://'+cfg['huginn']['url']+'/users/2/web_requests/'+cfg['huginn']['webrequest']['zhihu']
        zhihu_data = request.get_data()
        zdict = json.loads(zhihu_data)
        print(zdict['url'])
        zurl = zdict['url']
        # zhh = zhihu.Zhihu(url=zurl,huginnUrl=huginnUrl)
        # zhh.get_fav_item()
        # requests.post(url=huginnUrl,data=zhh.get_fav_item())
        return '1'

    @server.route('/inoreaderConvert', methods=['get','post'])
    def inoreaderConvert():
        try:
            inoreader_data = request.get_data()
            idict = json.loads(inoreader_data)
            print(idict)
            tdict = {
                'content' : idict['content'],
                'title' : idict['title'],
                'origin' : idict['origin'],
                'originurl': idict['originurl'],
                'url' : idict['aurl']
            }
            print(tdict)
            # t_url = requests.post(url=telegraph_url, json=tdict).text
            t_url = util.telegraphConvert(tdict)
            mdict = {
                'category' : idict['tag'],
                'title' : idict['title'],
                'origin' : idict['origin'],
                'aurl' : idict['aurl'],
                'originurl': idict['originurl'],
                'message': idict['message']+'\n' if idict['message'] else '',
                'turl': t_url
            }
            print(mdict)
            atelebot.send_to_channel(mdict)
        except Exception:
            print(traceback.format_exc())
            return 'Failed'
        return mdict

    @server.route('/telegraphConvert', methods=['get', 'post'])
    def telegraphConvert(check=True):
        res = ''
        #url = 'https://'+cfg['huginn']['url']+'/users/2/web_requests/'+cfg['huginn']['webrequest']['telegraph']
        #definite the keys of the json file
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
                telegraphPost = t.post(title=metadata_dict['title'], author=metadata_dict[author], text=metadata_dict['content'], author_url=metadata_dict[author_url])
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
    # 开启telebot线程
    telebot_thread = threading.Thread(target=atelebot.bot.polling, daemon=True)
    telebot_thread.start()  # start the bot in a thread instead
    # 豆瓣收藏夹
    # durl = 'https://www.douban.com/doulist/145693559/'
    # d = douban.Douban(durl)
    # class RepeatingTimer(threading.Timer):
    #     def run(self):
    #         while not self.finished.is_set():
    #             self.function(*self.args, **self.kwargs)
    #             self.finished.wait(self.interval)
    # t = RepeatingTimer(10.0,d.get_fav_list)
    # t.start()
    return server
