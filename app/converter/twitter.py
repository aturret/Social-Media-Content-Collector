import json
import requests
from collections import OrderedDict
from lxml import etree, html
import sys
from app import settings
import re

X_RapidAPI_Key = settings.env_var.get('X_RAPIDAPI_KEY', '')
tpattern = re.compile(r'(?<=status/)[0-9]*')  # 摘出推文id
twitter154_headers = {
    "content-type": "application/octet-stream",
    "X-RapidAPI-Key": X_RapidAPI_Key,
    "X-RapidAPI-Host": "twitter154.p.rapidapi.com"
}
twitter135_headers = {
    "content-type": "application/octet-stream",
    "X-RapidAPI-Key": X_RapidAPI_Key,
    "X-RapidAPI-Host": "twitter135.p.rapidapi.com"
}


# 编辑推送信息


class Twitter(object):
    def __init__(self, url, **kwargs):
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
        self.scraper = kwargs['api_method'] if 'api_method' in kwargs else 'Twitter135'
        if self.scraper == 'Twitter154':
            self.api_url = 'https://twitter154.p.rapidapi.com/tweet/details'
            self.headers = twitter154_headers
        if self.scraper == 'Twitter135':
            self.api_url = 'https://twitter135.p.rapidapi.com/v2/TweetDetail/'
            self.headers = twitter135_headers
        # twitter contents
        self.tid = tpattern.search(self.url).group()
        self.content = ''
        self.text = ''
        self.media_files = []

    def to_dict(self):
        self_dict = {}
        for k, v in self.__dict__.items():
            if k == 'headers':
                continue
            self_dict[k] = v
        return self_dict

    def get_single_tweet(self):
        if self.scraper == 'Official':
            api_info = self.get_tweet_official()
            self.tweet_process_official(api_info)
        elif self.scraper == 'Twitter154':
            api_info = self.get_tweet_Twitter154()
            self.tweet_process_Twitter154(api_info)
        elif self.scraper == 'Twitter135':
            api_info = self.get_tweet_Twitter135()
            self.tweet_process_Twitter135(api_info)
        twitter_item = self.to_dict()
        print(twitter_item)
        return twitter_item

    def get_tweet_official(self):
        tid = tpattern.search(self.url).group()
        tapiurl = 'https://api.twitter.com/2/tweets/' + tid
        response = requests.get(url=tapiurl, headers=self.headers, params=self.params).json()
        return response

    def tweet_process_official(self,tweet_info):
        self.text = tweet_info['data']['text']
        self.origin = tweet_info['includes']['users'][0]['name']
        self.title = self.origin + '\'s tweet'
        self.originurl = 'https://twitter.com/' + tweet_info['includes']['users'][0]['username']
        self.aurl = self.url
        self.media_files = []
        picformat = ''  # 处理图片
        if 'attachments' in tweet_info['data']:
            for i in tweet_info['includes']['media']:
                picformat += '<img src="' + i['url'] + '">' + '<br>'
                media_item = {'type': 'image', 'url': i['url'], 'caption': ''}
                self.media_files.append(media_item)
            print(picformat)
        self.content = self.text + '<br>' + picformat
        self.text = '<a href="' + self.url + '">@' + self.origin + '</a>: ' + self.text
        self.type = 'long' if len(html.fromstring(self.text).xpath('string()')) > 200 else 'short'


    def get_tweet_Twitter135(self):
        response = requests.get(url=self.api_url, headers=self.headers, params={'id': self.tid}).json()
        return response

    def tweet_process_Twitter135(self, api_info):
        entries = api_info['data']['threaded_conversation_with_injections_v2']['instructions'][0]['entries']
        tweets = []
        for i in entries:
            if i['content']['entryType'] == 'TimelineTimelineItem':
                if i['content']['itemContent']['itemType'] == 'TimelineTweet':
                    tweets.append(i['content']['itemContent']['tweet_results']['result'])
        for tweet in tweets:
            if tweet['legacy']['id_str'] == self.tid:
                self.origin = tweet['core']['user_results']['result']['legacy']['name']
                self.title = self.origin + '\'s tweet'
                self.originurl = 'https://twitter.com/' + tweet['core']['user_results']['result']['legacy'][
                    'screen_name']
                self.aurl = self.url
                self.date = tweet['legacy']['created_at']
                picformat = ''
                self.content += 'created at: ' + self.date + '<br>'
        for tweet in tweets:
            tweet_info = self.single_tweet_process_Twitter135(tweet)
            self.content += tweet_info['content'] + '<hr>'
            self.text += '<a href=\"' + tweet_info['aurl'] + '">@' + tweet_info['origin'] + '</a>: ' + tweet_info[
                'text'] + '\n'
        self.type = 'long' if len(self.text) > 300 else 'short'
        self.tweet_raw_text_to_html()






    def single_tweet_process_Twitter135(self,tweet):
        tweet_info = {}
        tweet_info['title'] = tweet['core']['user_results']['result']['legacy']['name'] + '\'s tweet'
        tweet_info['origin'] = tweet['core']['user_results']['result']['legacy']['name']
        tweet_info['originurl'] = 'https://twitter.com/' + tweet['core']['user_results']['result']['legacy']['screen_name']
        tweet_info['aurl'] = 'https://twitter.com/' + tweet['core']['user_results']['result']['legacy']['screen_name'] + '/status/' + tweet['legacy']['id_str']
        tweet_info['text'] = tweet['note_tweet']['note_tweet_results']['result']['text'] if 'note_tweet' in tweet else tweet['legacy']['full_text']
        tweet_info['content'] = tweet_info['text'] + '<br>'
        if 'extended_entities' in tweet['legacy']:
            for i in tweet['legacy']['extended_entities']['media']:
                if i['type'] == 'photo':
                    tweet_info['content'] += '<img src="' + i['media_url_https'] + '">' + '<br>'
                    media_item = {'type': 'image', 'url': i['media_url_https'], 'caption': ''}
                if i['type'] == 'video':
                    highest_bitrate_item = max(i['video_info']['variants'], key=lambda x: x.get('bitrate', 0))
                    tweet_info['content'] += '<video controls="controls" src="' + highest_bitrate_item['url'] + '">' + '<br>'
                    media_item = {'type': 'video', 'url': highest_bitrate_item['url'], 'caption': ''}
                self.media_files.append(media_item)
        return tweet_info

    def tweet_raw_text_to_html(self):
        def replace_url(match):
            url = match.group(0)
            before_url = match.group(1)
            if before_url == '<':
                return match.group(0)
            else:
                return f'<a href="{url}">{url}</a>'
        content = self.content
        parts = re.split(r'\n+', content)
        content = ''.join([f'<p>{part}</p>' for part in parts])
        content = re.sub(r'(<)?https:\/\/t\.co\/[\w-]+', replace_url, content)
        self.content = content
