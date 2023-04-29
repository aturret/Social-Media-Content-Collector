from app.utils.util import *
import re

X_RapidAPI_Key = settings.env_var.get('X_RAPIDAPI_KEY', '')
# tpattern = re.compile(r'(?<=status/)[0-9]*')
all_scrapers = ['ins28', 'scraper2', 'looter2']
all_story_scrapers = ['stories1', 'scraper2022']

class Instagram(object):
    def __init__(self, url, **kwargs):
        self.url = url
        self.status = False
        self.aurl = re.sub(r"/\?.*", "/", self.url)
        self.post_id = re.sub(r".*[(/p/)(/reel/)]", "", self.aurl).replace('/', '')
        self.params = {
        }
        self.scraper = kwargs['scraper'] if 'scraper' in kwargs else 'looter2'
        self.story_scraper = kwargs['story_scraper'] if 'story_scraper' in kwargs else 'stories1'
        # twitter contents
        self.content = ''
        self.text = ''
        self.media_files = []
        self.type = ''
        # headers

    def to_dict(self):
        self_dict = {}
        for k, v in self.__dict__.items():
            if k == 'headers':
                continue
            self_dict[k] = v
        return self_dict

    def get_single_ins_item(self):
        if self.url.find('instagram.com/p/') != -1 or self.url.find('instagram.com/reel/') != -1:
            return self.get_ins_post_item()
        if self.url.find('instagram.com/stories/') != -1:
            return self.get_ins_story_item()
        return self.to_dict()

    def get_ins_post_item(self):
        ins_info = {}
        for scraper in all_scrapers:
            self.scraper = scraper
            self.process_get_media_headers()
            response = requests.get(self.host, headers=self.headers, params=self.params)
            if response.status_code != 200:
                print('get_ins_post_item error: ', self.scraper, response.status_code)
                continue
            else:
                ins_data = response.json()
                print(ins_data)
                print(self.params)
                if type(ins_data) == dict and 'status' not in ins_data or ins_data['status'] is False:
                    print('get_ins_post_item error: ', self.scraper)
                    continue
                elif type(ins_data) == str and '400' in ins_data:
                    print('get_ins_post_item error: ', self.scraper, ins_data)
                    continue
            if self.scraper == 'looter2':
                ins_info = self.get_ins_post_looter2(ins_data)
            elif self.scraper == 'ins28' or self.scraper == 'scraper2':
                ins_info = self.get_ins_post_ins28_scraper2(ins_data)
        if ins_info is not None:
            self.ins_post_item_process(ins_info)
        return self.to_dict()

    def process_get_media_headers(self):
        if self.scraper == 'looter2':
            self.host = 'https://instagram-looter2.p.rapidapi.com/post'
            self.scraper_top_domain = 'instagram-looter2'
            self.params = {'link': self.url}
        elif self.scraper == 'ins28':
            self.host = 'https://instagram28.p.rapidapi.com/media_info_v2'
            self.scraper_top_domain = 'instagram28'
            self.params = {'short_code': self.post_id}
        elif self.scraper == 'scraper2':
            self.host = 'https://instagram-scraper2.p.rapidapi.com/media_info_v2'
            self.scraper_top_domain = 'instagram-scraper2'
            self.params = {'short_code': self.post_id}
        self.headers = {
            'X-RapidAPI-Key': X_RapidAPI_Key,
            'X-RapidAPI-Host': self.scraper_top_domain + '.p.rapidapi.com',
            "content-type": "application/octet-stream",
        }

    def ins_post_item_process(self, ins_info):
        self.__dict__.update(ins_info)
        self.title = self.origin + '\'s Instagram post'
        self.text = "<a href='" + self.aurl + "'>" + self.title + "</a>\n" + self.text
        self.type = 'short' if len(self.text) < 300 else 'long'

    def get_ins_post_looter2(self, ins_data):
        ins_info = {}
        ins_info['content'] = ins_data['edge_media_to_caption']['edges'][0]['node']['text'] if ins_data[
            'edge_media_to_caption']['edges'] else ''
        ins_info['text'] = ins_info['content']
        ins_info['origin'] = ins_data['owner']['username'] + '(' + ins_data['owner']['full_name'] + ')'
        ins_info['originurl'] = 'https://www.instagram.com/' + ins_data['owner']['username'] + '/'
        ins_info['media_files'] = []
        if ins_data['__typename'] == 'GraphVideo':
            ins_info['media_files'].append({'type': 'video', 'url': ins_data['video_url'], 'caption': ''}) if ins_data[
                'video_url'] else []
            ins_info['content'] += '<video controls src="' + ins_data['video_url'] + '"></video>'
        elif ins_data['__typename'] == 'GraphSidecar':
            for item in ins_data['edge_sidecar_to_children']['edges']:
                if item['node']['__typename'] == 'GraphVideo':
                    ins_info['media_files'].append({'type': 'video', 'url': item['node']['video_url'], 'caption': ''})
                    ins_info['content'] += '<video controls src="' + item['node']['video_url'] + '"></video>'
                elif item['node']['__typename'] == 'GraphImage':
                    ins_info['media_files'].append({'type': 'image', 'url': item['node']['display_url'], 'caption': ''})
                    ins_info['content'] += '<img src="' + item['node']['display_url'] + '">'
        ins_info['status'] = True
        return ins_info

    def get_ins_post_ins28_scraper2(self, ins_data):
        ins_info = {}
        ins_info['content'] = ins_data['items'][0]['caption']['text'] if ins_data['items'][0]['caption'] else ''
        ins_info['text'] = ins_info['content']
        ins_info['origin'] = ins_data['items'][0]['user']['username'] + '(' + ins_data['items'][0]['user']['full_name'] + ')'
        ins_info['originurl'] = 'https://www.instagram.com/' + ins_data['items'][0]['user']['username'] + '/'
        ins_info['media_files'] = []
        if ins_data['items'][0]['media_type'] == 2:
            ins_info['media_files'].append({'type': 'video', 'url': ins_data['items'][0]['video_versions'][0]['url'], 'caption': ''})
            ins_info['content'] += '<video controls src="' + ins_data['items'][0]['video_versions'][0]['url'] + '"></video>'
        elif ins_data['items'][0]['media_type'] == 8:
            for item in ins_data['items'][0]['carousel_media']:
                if item['media_type'] == 2:
                    ins_info['media_files'].append({'type': 'video', 'url': item['video_versions'][0]['url'], 'caption': ''})
                    ins_info['content'] += '<video controls src="' + item['video_versions'][0]['url'] + '"></video>'
                elif item['media_type'] == 1:
                    ins_info['media_files'].append({'type': 'image', 'url': item['image_versions2']['candidates'][0]['url'], 'caption': ''})
                    ins_info['content'] += '<img src="' + item['image_versions2']['candidates'][0]['url'] + '">'
        ins_info['status'] = True
        return ins_info

    def get_ins_story_item(self):
        if self.story_scraper == 'stories1':
            self.get_ins_story_stories1()
        if self.story_scraper == 'scraper2022':
            self.get_ins_story_scraper2022()
        self.ins_story_item_process()
        return self.to_dict()

    def process_get_story_headers(self):
        if self.story_scraper == 'stories1':
            self.story_host = 'https://instagram-stories1.p.rapidapi.com/'
            self.story_scraper_top_domain = 'instagram-stories1'
        elif self.story_scraper == 'scraper2022':
            self.story_host = 'https://instagram-scraper-2022.p.rapidapi.com/'
            self.story_scraper_top_domain = 'instagram-scraper-2022'
        self.headers = {
            'X-RapidAPI-Key': X_RapidAPI_Key,
            'X-RapidAPI-Host': self.story_scraper_top_domain + '.p.rapidapi.com',
            "content-type": "application/octet-stream",
        }