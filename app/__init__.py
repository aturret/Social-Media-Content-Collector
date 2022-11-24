# -*- coding:utf-8 -*-
from flask import Flask
import json
from flask import request
from html_telegraph_poster import TelegraphPoster
import requests
import re
import threading
from . import atelebot, weibo, douban, zhihu, telegraph, combination, util
from collections import OrderedDict
import traceback
from time import sleep
import toml


# from .verify import check


def create_app():
    server = Flask(__name__)
    list = [""]
    server.config.from_prefixed_env()
    server.config.from_file("./config.toml", load=toml.load)
    print(server.config)
    cfg = server.config
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
        huginnUrl='https://'+cfg['huginn']['url']+'/users/2/web_requests/'+cfg['huginn']['webrequest']['weibo']
        weiboData = request.get_data()
        wdict = json.loads(weiboData)
        print(wdict['url'])
        wurl = wdict['url']
        if wurl.find('weibo.com'):
            wurl=wurl.replace('weibo.com','m.weibo.cn')
        wb = weibo.Weibo(wurl)
        # print(wb.get_weibo())
        requests.post(url=huginnUrl,data=wb.get_weibo())
        return wb.get_weibo()

    @server.route('/doubanConvert', methods=['get', 'post'])
    def doubanConvert():
        huginnUrl = 'https://'+cfg['huginn']['url']+'/users/2/web_requests/'+cfg['huginn']['webrequest']['douban']
        doubanData = request.get_data()
        ddict = json.loads(doubanData)
        print(ddict['url'])
        durl = ddict['url']
        db = douban.Douban(url=durl,huginnUrl=huginnUrl)
        db.get_fav_item(url=db.url)
        return db.get_fav_item()

    @server.route('/twitterConvert', methods=['get', 'post'])
    def twitterConvert():
        huginnUrl = 'https://'+cfg['huginn']['url']+'/users/2/web_requests/'+cfg['huginn']['webrequest']['twitter']
        headers = {
            'Authorization' : 'Bearer '+cfg['authorization']['twitter']['app_key'],
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
        requests.post(url=huginnUrl,data=twitter)
        return reqs

    @server.route('/zhihuConvert', methods=['get', 'post'])
    def zhihuConvert():
        huginnUrl='https://'+cfg['huginn']['url']+'/users/2/web_requests/'+cfg['huginn']['webrequest']['zhihu']
        zhihuData = request.get_data()
        zdict = json.loads(zhihuData)
        print(zdict['url'])
        zurl = zdict['url']
        zhh = zhihu.Zhihu(url=zurl,huginnUrl=huginnUrl)
        zhh.get_fav_item()
        # requests.post(url=huginnUrl,data=zhh.get_fav_item())
        return '1'

    @server.route('/telegraphConvert', methods=['get', 'post'])
    def telegraphConvert(check=True):
        url = 'https://'+cfg['huginn']['url']+'/users/2/web_requests/'+cfg['huginn']['webrequest']['telegraph'] # huginn webhook
        #definite the keys of the json file
        author = 'origin'
        author_url = 'originurl'
        article_url = 'aurl'
        title = 'title'
        content = 'content'
        broadcastData = request.get_data()
        dict = json.loads(broadcastData)
        print(dict[title])
        # Use pyhtmltotelegraph to post telegraph article
        def post():
            try:
                t = TelegraphPoster(use_api=True)
                short_name = dict[author]
                t.create_api_token(short_name[0:14],author_name=dict[author])
                telegraphPost = t.post(title=dict[title], author=dict[author], text=dict[content],author_url=dict[author_url])
                print(telegraphPost['url'])
                print(type(telegraphPost))
                telegraphPostJSON = {'url': ''}
                telegraphPostJSON['url'] = telegraphPost['url']
                r = requests.post(url=url, data=telegraphPostJSON)
                print(r.text)
            except Exception:
                print(traceback.format_exc())
        print(list)
        # 如果开启check标记，检测标题是否重复，如果重复就不发了
        if check:
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
        else:
            post()
        return ('mission accomplished')
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
