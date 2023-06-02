from app.utils import util
from app import settings
import requests
import re
import httpx

X_RapidAPI_Key = settings.env_var.get('X_RAPIDAPI_KEY', '')
tpattern = re.compile(r'(?<=status/)[0-9]*')  # 摘出推文id
ALL_SCRAPER = ['Twitter135', 'Twitter154']
ALL_SINGLE_SCRAPER = ['Twitter154']


# 编辑推送信息


class Twitter(object):
    def __init__(self, url, **kwargs):
        self.host = None
        self.top_domain = None
        self.url = url
        self.aurl = url
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
        self.scraper_type = kwargs['scraper_type'] if 'scraper_type' in kwargs else 'thread'
        self.scraper = ''
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

    async def get_tweet_item(self):
        await self.get_single_tweet()
        twitter_item = self.to_dict()
        print(twitter_item)
        return twitter_item

    def get_tweet_official(self):
        tid = tpattern.search(self.url).group()
        tapiurl = 'https://api.twitter.com/2/tweets/' + tid
        response = requests.get(url=tapiurl, headers=self.headers, params=self.params).json()
        return response

    def tweet_process_official(self, tweet_info):
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
        self.type = 'long' if util.get_html_text_length(self.text) > 200 else 'short'

    async def get_single_tweet(self):
        tweet_info = {}
        used_scraper = ALL_SINGLE_SCRAPER if self.scraper_type == 'single' else ALL_SCRAPER
        for scraper in used_scraper:
            if self.scraper == '':
                self.scraper = scraper
            print('using scraper: ', self.scraper)
            self.process_get_media_headers()
            async with httpx.AsyncClient() as client:
                response = await client.get(url=self.host, headers=self.headers, params=self.params)
            if response.status_code == 200:
                tweet_data = response.json()
                print(tweet_data, self.params)
                if (type(tweet_data) == dict and ('errors' in tweet_data or 'detail' in tweet_data)) or \
                        (type(tweet_data) == str and '400' in tweet_data):
                    print('get tweet error: ', self.scraper, tweet_data)
                    continue
                else:
                    break
            else:
                print('get tweet error: ', self.scraper, response.status_code)
                continue
        if self.scraper == 'Twitter154':
            tweet_info = self.tweet_process_Twitter154(tweet_data)
        elif self.scraper == 'Twitter135' or self.scraper == 'twitter-v24':
            tweet_info = self.tweet_process_Twitter135(tweet_data)
        if tweet_info is not None:
            self.tweet_item_process(tweet_info)

    def tweet_item_process(self, tweet_info):
        self.origin = tweet_info['origin']
        self.title = tweet_info['origin'] + '\'s tweet'
        self.originurl = tweet_info['originurl']
        self.aurl = self.url
        self.date = tweet_info['date']
        self.content = tweet_info['content']
        self.text = tweet_info['text']
        self.type = 'long' if len(self.text) > 300 else 'short'
        self.media_files = tweet_info['media_files'] if 'media_files' in tweet_info else []
        self.tweet_raw_text_to_html()

    def tweet_process_Twitter135(self, tweet_data):
        tweet_info = {}
        entries = tweet_data['data']['threaded_conversation_with_injections_v2']['instructions'][0]['entries']
        tweets = []
        for i in entries:
            if i['content']['entryType'] == 'TimelineTimelineItem':
                if i['content']['itemContent']['itemType'] == 'TimelineTweet':
                    tweets.append(i['content']['itemContent']['tweet_results']['result'])
        for tweet in tweets:
            if tweet['__typename'] == 'Tweet':
                if tweet['rest_id'] == self.tid:
                    tweet_result = tweet
                else:
                    continue
            elif tweet['__typename'] == 'TweetWithVisibilityResults':
                if tweet['tweet']['rest_id'] == self.tid:
                    tweet_result = tweet['tweet']
                else:
                    continue
            else:
                continue
            tweet_info['origin'] = tweet_result['core']['user_results']['result']['legacy']['name']
            tweet_info['originurl'] = 'https://twitter.com/' + tweet_result['core']['user_results']['result']['legacy'][
                'screen_name']
            tweet_info['date'] = tweet_result['legacy']['created_at']
            tweet_info['content'] = 'created at: ' + tweet_info['date'] + '<br>'
            tweet_info['text'] = ''
        tweet_info['media_files'] = []
        for tweet in tweets:
            single_tweet_info = self.single_tweet_process_Twitter135(tweet)
            if self.scraper_type == 'single' and single_tweet_info['tid'] != self.tid:
                continue
            tweet_info['media_files'] += single_tweet_info['media_files']
            tweet_info['content'] += single_tweet_info['content'] + '<hr>'
            tweet_info['text'] += '<a href=\"' + single_tweet_info['aurl'] + '">@' + single_tweet_info['origin'] + \
                                  '</a>: ' + single_tweet_info['text']
        return tweet_info

    def single_tweet_process_Twitter135(self, tweet):
        single_tweet_info = {}
        if tweet['__typename'] == 'TweetWithVisibilityResults':
            tweet = tweet['tweet']
        single_tweet_info['tid'] = tweet['rest_id']
        single_tweet_info['title'] = tweet['core']['user_results']['result']['legacy']['name'] + '\'s tweet'
        single_tweet_info['origin'] = tweet['core']['user_results']['result']['legacy']['name']
        single_tweet_info['originurl'] = 'https://twitter.com/' + \
                                         tweet['core']['user_results']['result']['legacy']['screen_name']
        single_tweet_info['aurl'] = 'https://twitter.com/' + \
                                    tweet['core']['user_results']['result']['legacy']['screen_name'] + \
                                    '/status/' + tweet['legacy']['id_str']
        single_tweet_info['text'] = tweet['note_tweet']['note_tweet_results']['result']['text'] \
            if 'note_tweet' in tweet else tweet['legacy']['full_text']
        single_tweet_info['text'] = util.escape(single_tweet_info['text'])
        single_tweet_info['content'] = single_tweet_info['text'] + '<br>'
        single_tweet_info['media_files'] = []
        if 'extended_entities' in tweet['legacy']:
            for media in tweet['legacy']['extended_entities']['media']:
                if media['type'] == 'photo':
                    single_tweet_info['content'] += '<img src="' + media['media_url_https'] + '">' + '<br>'
                    media_item = {'type': 'image', 'url': media['media_url_https'], 'caption': ''}
                if media['type'] == 'video':
                    highest_bitrate_item = max(media['video_info']['variants'], key=lambda x: x.get('bitrate', 0))
                    single_tweet_info['content'] += '<video controls="controls" src="' + \
                                                    highest_bitrate_item['url'] + '">' + '<br>'
                    media_item = {'type': 'video', 'url': highest_bitrate_item['url'], 'caption': ''}
                single_tweet_info['media_files'].append(media_item)
        return single_tweet_info

    def tweet_process_Twitter154(self, tweet_data):
        tweet_info = {}
        tweet_info['origin'] = tweet_data['user']['name']
        tweet_info['originurl'] = 'https://twitter.com/' + tweet_data['user']['username']
        tweet_info['date'] = tweet_data['creation_date']
        tweet_info['content'] = 'created at: ' + tweet_info['date'] + '<br>'
        tweet_info['text'] = '<a href=\"' + self.aurl + '">@' + tweet_info['origin'] + \
                             '</a>: ' + tweet_data['text']
        tweet_info['media_files'] = []
        if 'extended_entities' in tweet_data and tweet_data['extended_entities'] is not None:
            for i in tweet_data['extended_entities']['media']:
                if i['type'] == 'photo':
                    tweet_info['content'] += '<img src="' + i['media_url_https'] + '">' + '<br>'
                    media_item = {'type': 'image', 'url': i['media_url_https'], 'caption': ''}
                if i['type'] == 'video':
                    highest_bitrate_item = max(i['video_info']['variants'], key=lambda x: x.get('bitrate', 0))
                    tweet_info['content'] += '<video controls="controls" src="' + highest_bitrate_item['url'] +\
                                             '">' + '<br>'
                    media_item = {'type': 'video', 'url': highest_bitrate_item['url'], 'caption': ''}
                tweet_info['media_files'].append(media_item)
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

    def process_get_media_headers(self):
        if self.scraper == 'Twitter154':
            self.host = 'https://twitter154.p.rapidapi.com/tweet/details'
            self.top_domain = 'twitter154'
            self.params = {'tweet_id': self.tid}
        elif self.scraper == 'Twitter135':
            self.host = 'https://twitter135.p.rapidapi.com/v2/TweetDetail/'
            self.top_domain = 'twitter135'
            self.params = {'id': self.tid}
        elif self.scraper == 'twitter-v24':
            self.host = 'https://twitter-v24.p.rapidapi.com/tweet/details'
            self.top_domain = 'twitter-v24'
            self.params = {'tweet_id': self.tid}
        self.headers = {
            'X-RapidAPI-Key': X_RapidAPI_Key,
            'X-RapidAPI-Host': self.top_domain + '.p.rapidapi.com',
            "content-type": "application/octet-stream",
        }
