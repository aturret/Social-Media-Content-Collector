# -*- coding:utf-8 -*-
from flask import Flask
import json
from flask import request
from html_telegraph_poster import TelegraphPoster
import requests
import re
import threading
from . import aturretbot, weibo, douban
from collections import OrderedDict
from time import sleep


# from .verify import check

'''
flask： web框架，通过flask提供的装饰器@server.route()将普通函数转换为服务
'''


# 创建一个服务，把当前这个python文件当做一个服务
def create_app():
    server = Flask(__name__)
    list = [""]


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
        huginnUrl='https://huginn.aturret.top/users/2/web_requests/56/shelleysmummydied'
        weiboData = request.get_data()
        wdict = json.loads(weiboData)
        print(wdict['url'])
        wurl = wdict['url']
        if wurl.find('weibo.com'):
            wurl=wurl.replace('weibo.com','m.weibo.cn')
        wb = weibo.Weibo(wurl)
        print(wb.get_weibo())
        requests.post(url=huginnUrl,data=wb.get_weibo())
        return wb.get_weibo()

    @server.route('/twitterConvert', methods=['get', 'post'])
    def twitterConvert():
        apiurl = 'https://huginn.aturret.top/users/2/web_requests/60/shelleysdaddydied'
        headers = {
            'Authorization' : 'Bearer AAAAAAAAAAAAAAAAAAAAANmlWAEAAAAAPk7fNFgO2P0Mg83ga4kVvF49ilI%3DL67pc1i9el1HNUo2vJOPFTts921jAd1QpFqp8XZYYIblJ7MLLU',
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
        tapiurl='https://api.twitter.com/2/tweets/' + tid# + '?expansions=referenced_tweets.id,referenced_tweets.id.author_id&tweet.fields=created_at'
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
        requests.post(url=apiurl,data=twitter)
        return reqs

    # @server.route('/doubanGet')
    # # 开启豆瓣抓取线程
    # def doubanGet():
    #     while True:
    #         d.get_fav_list()
    #         print('1')
    #         sleep(5)


    @server.route('/telegraphConvert', methods=['get', 'post'])
    def telegraphConvert():
        url = 'https://huginn.aturret.top/users/2/web_requests/21/supersbshelley' # huginn webhook
        #definite the keys of the json file
        author = 'origin'
        author_url = 'originurl'
        article_url = 'aurl'
        title = 'title'
        content = 'content'
        broadcastData = request.get_data()
        dict = json.loads(broadcastData)
        print(dict[title])
        # Use htmltotelegraph to post telegraph article
        def post():
            t = TelegraphPoster(use_api=True)
            short_name = dict[author]
            t.create_api_token(short_name[0:14], dict[author], dict[article_url])
            a = t.post(dict[title], dict[author], dict[content])
            print(a['url'])
            b = {'url': ''}
            b['url'] = a['url']
            r = requests.post(url=url, data=b)
            print(r.text)
        print(list)
        # 检测标题是否重复，如果重复就不发了
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
        return ('mission accomplished')
    # 开启telebot线程
    telebot_thread = threading.Thread(target=aturretbot.bot.polling, daemon=True)
    telebot_thread.start()  # start the bot in a thread instead
    durl = 'https://www.douban.com/doulist/145693559/'
    d = douban.Douban(durl)
    def getDouban():
        d.get_fav_list()
        print('1')
        threading.Timer(3, getDouban).start()
    getDouban()



# douban_thread = threading.Timer(5, d.get_fav_list)
    # douban_thread.start()
    return server
