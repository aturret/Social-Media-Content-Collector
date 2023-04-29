from app.utils.util import *
import re

X_RapidAPI_Key = settings.env_var.get('X_RAPIDAPI_KEY', '')
# tpattern = re.compile(r'(?<=status/)[0-9]*')


class Instagram(object):
    def __init__(self, url, **kwargs):
        self.url = url
        self.status = False
        self.params = {
        }
        self.scraper = kwargs['scraper'] if 'scraper' in kwargs else 'looter2'
        self.story_scraper = kwargs['story_scraper'] if 'story_scraper' in kwargs else 'stories1'
        if self.scraper == 'looter2':
            self.host = 'https://instagram-looter2.p.rapidapi.com/'
            self.scraper_top_domain = 'instagram-looter2'
            self.params = {'link': self.url}
        if self.scraper == 'ins28':
            self.host = 'https://instagram28.p.rapidapi.com/'
            self.scraper_top_domain = 'instagram28'

        if self.scraper == 'scraper2':
            self.host = 'https://instagram-scraper2.p.rapidapi.com/'
            self.scraper_top_domain = 'instagram-scraper2'
        if self.story_scraper == 'stories1':
            self.story_host = 'https://instagram-stories1.p.rapidapi.com/'
            self.story_scraper_top_domain = 'instagram-stories1'
        if self.story_scraper == 'scraper2022':
            self.story_host = 'https://instagram-scraper-2022.p.rapidapi.com/'
            self.story_scraper_top_domain = 'instagram-scraper-2022'
        # twitter contents
        self.content = ''
        self.text = ''
        self.aurl = re.sub(r"/\?.*", "/", self.url)
        self.media_files = []
        self.type = ''
        # headers
        self.headers = {
            # 'Cookie': '',
            # 'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Redmi K30 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.185 Mobile Safari/537.36',
            'X-RapidAPI-Key': X_RapidAPI_Key,
            'X-RapidAPI-Host': self.scraper_top_domain + '.p.rapidapi.com',
            "content-type": "application/octet-stream",
        }

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
        if self.scraper == 'looter2':
            ins_info = self.get_ins_post_looter2()
        if self.scraper == 'ins28':
            ins_info = self.get_ins_post_ins28()
        if self.scraper == 'scraper2':
            ins_info = self.get_ins_post_scraper2()
        self.ins_post_item_process(ins_info)
        return self.to_dict()

    def ins_post_item_process(self, ins_info):
        self.__dict__.update(ins_info)
        self.title = self.origin + '\'s Instagram post'
        self.text = "<a href='"+self.aurl+"'>"+self.title+"</a>\n" + self.text
        self.type = 'short' if len(self.text) < 300 else 'long'

    def get_ins_post_looter2(self):
        response = requests.get(self.host+'post', headers=self.headers, params=self.params)
        print(response.status_code)
        print(response.json())
        if response.status_code != 200 or response.json()['status']==False:
            return {}
        ins_info = {}
        ins_data = response.json()
        ins_info['content'] = ins_data['edge_media_to_caption']['edges'][0]['node']['text'] if ins_data[
            'edge_media_to_caption']['edges'] else ''
        ins_info['text'] = ins_info['content']
        ins_info['origin'] = ins_data['owner']['username']+'('+ins_data['owner']['full_name']+')'
        ins_info['originurl'] = 'https://www.instagram.com/'+ins_data['owner']['username']+'/'
        ins_info['media_files'] = []
        if ins_data['__typename'] == 'GraphVideo':
            ins_info['media_files'] = [{'type': 'video', 'url': ins_data['video_url'], 'caption': ''}] if ins_data[
                'video_url'] else []
            ins_info['content'] += '<video controls src="'+ins_data['video_url']+'"></video>'
        elif ins_data['__typename'] == 'GraphSidecar':
            for item in ins_data['edge_sidecar_to_children']['edges']:
                if item['node']['__typename'] == 'GraphVideo':
                    ins_info['media_files'].append({'type': 'video', 'url': item['node']['video_url'], 'caption': ''})
                    ins_info['content'] += '<video controls src="'+item['node']['video_url']+'"></video>'
                elif item['node']['__typename'] == 'GraphImage':
                    ins_info['media_files'].append({'type': 'image', 'url': item['node']['display_url'], 'caption': ''})
                    ins_info['content'] += '<img src="'+item['node']['display_url']+'">'
        ins_info['status'] = True
        return ins_info


    def get_ins_story_item(self):
        if self.story_scraper == 'stories1':
            self.get_ins_story_stories1()
        if self.story_scraper == 'scraper2022':
            self.get_ins_story_scraper2022()
        self.ins_story_item_process()
        return self.to_dict()


