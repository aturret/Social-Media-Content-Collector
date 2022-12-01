import json
import requests
from collections import OrderedDict
from lxml import etree
import sys
from . import settings
import re

tpattern = re.compile(r'(?<=status/)[0-9]*')  # 摘出推文id


# 编辑推送信息

class Twitter(object):
    def __init__(self, url):
        self.url = url
        self.headers = {
            'Authorization': 'Bearer ' + settings.env_var.get('TWITTER_APP_KEY'),
            'Cookie': '',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
        }
        self.params = {
            'expansions': 'referenced_tweets.id,referenced_tweets.id.author_id,attachments.media_keys',
            'tweet.fields': 'created_at',
            'media.fields': 'duration_ms,height,media_key,preview_image_url,public_metrics,type,url,width,alt_text'
        }

    def get_single_tweet(self):
        twitter_item = OrderedDict()
        tid = tpattern.search(self.url).group()
        tapiurl = 'https://api.twitter.com/2/tweets/' + tid
        reqs = requests.get(url=tapiurl, headers=self.headers, params=self.params).json()
        twitter_item['text'] = reqs['data']['text']
        twitter_item['origin'] = reqs['includes']['users'][0]['name']
        twitter_item['title'] = twitter_item['origin'] + '\'s tweet'
        twitter_item['originurl'] = 'https://twitter.com/' + reqs['includes']['users'][0]['username']
        twitter_item['aurl'] = self.url
        picformat = ''  # 处理图片
        if 'attachments' in reqs['data']:
            for i in reqs['includes']['media']:
                picformat += '<img src="' + i['url'] + '">' + '<br>'
            print(picformat)
        twitter_item['content'] = twitter_item['text'] + '<br>' + picformat
        print(twitter_item)
        return twitter_item
