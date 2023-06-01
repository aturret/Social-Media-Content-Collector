import re
import traceback

import requests
import tempfile
import os
import yt_dlp
import youtube_dl
from app.settings import env_var
from app.utils import util

TEMP_DIR = env_var.get('TEMP_DIR', tempfile.gettempdir())
print(TEMP_DIR)
BILIBILI_COOKIE = None
bilibili_cookie_path = os.path.join(env_var.get('PWD', None), 'conf', 'www.bilibili.com_cookies.txt')
if os.path.exists(bilibili_cookie_path):
    BILIBILI_COOKIE = bilibili_cookie_path


class VideoConverter(object):
    def __init__(self, url, **kwargs):
        self.url = url
        self.parse_video_url()
        self.aurl = self.url
        self.ydl_opts = {
            'paths': {
                'home': TEMP_DIR
            },
            'outtmpl': {
                'default': '%(title)s-%(id)s.%(ext)s',
            },
        }
        self.scraper = kwargs.get('scraper', 'yt_dlp')
        self.download = kwargs.get('download', True)
        self.file_download = kwargs.get('file_download', False)
        self.hd = kwargs.get('hd', False)
        self.type = 'short'


    def to_dict(self):
        self_dict = {}
        for k, v in self.__dict__.items():
            if k == 'headers':
                continue
            self_dict[k] = v
        return self_dict

    def get_video_item(self):
        video_info = self.get_video_info()
        self.video_info_formatting(video_info)
        return self.to_dict()

    def get_video_info(self):
        if self.scraper == 'youtube_dl':
            with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                video_info = ydl.extract_info(self.url, download=self.file_download)
        elif self.scraper == 'yt_dlp':
            if self.extractor == 'BiliBili':
                if self.hd and BILIBILI_COOKIE:
                    self.ydl_opts['cookiefile'] = BILIBILI_COOKIE
                else:
                    self.ydl_opts['format'] = 'bv*[height<=480]+ba/b[height<=480] / wv*+ba/w'
            if self.extractor == 'youtube':
                if self.hd:
                    self.ydl_opts[
                        'format'] = 'bestvideo[ext=mp4]+(258/256/140)/best'
                else:
                    self.ydl_opts['format'] = 'bv*[height<=480]+ba/b[height<=480] / wv*+ba/w'
                self.file_download = True
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                video_info = ydl.extract_info(self.url, download=self.file_download, process=self.file_download)
        print(video_info)
        return video_info

    def video_info_formatting(self, video_info):
        """
        :param video_info: the video info from get_video_info(), which is originally from youtube_dl
        :return: this will directly modify the self object, no return
        """
        if video_info['extractor'] == 'BiliBili':
            self.category = 'Bilibili'
            meta_info = self.get_bilibili_video_info(video_info)
        elif video_info['extractor'] == 'youtube':
            self.category = 'YouTube'
            meta_info = self.get_youtube_video_info(video_info)
        else:
            return
        self.title = meta_info['title']
        self.origin = meta_info['author']
        self.originurl = meta_info['author_url']
        if len(meta_info['description']) > 800:
            meta_info['description'] = meta_info['description'][:800] + '...'
        self.created = meta_info['upload_date']
        self.duration = meta_info['duration']
        self.text = \
            '<a href=\"' + self.url + '\"><b>' + self.title + '</b></a>\n' + \
            '作者：<a href=\"' + self.originurl + '\">' + self.origin + '</a>\n' + \
            '视频时长：' + self.duration + '\n' + \
            '视频上传日期：' + self.created + '\n' + \
            '播放数据：' + meta_info['playback_data'] + '\n' + \
            '视频简介：' + meta_info['description'] + '\n'
        if self.download:
            if self.file_download:
                self.video_url = os.path.join(TEMP_DIR,
                                              meta_info['title'] + '-' + meta_info['id'] + '.' + meta_info['ext'])
                self.video_url = self.video_url.replace('|', '｜')
                video_download_text = ''
            else:
                if self.hd:
                    print('download hd video, this may take a while')
                    video_path, audio_path = None, None
                    print(meta_info['raw_video_content_infos'], meta_info['audio_content_infos'])
                    for item in meta_info['raw_video_content_infos']:
                        video_path = util.download_file(item['url'], extension=item['ext'])
                        if video_path is None:
                            continue
                        break
                    for item in meta_info['audio_content_infos']:
                        audio_path = util.download_file(item['url'], extension=item['ext'])
                        if audio_path is None:
                            continue
                        break
                    if video_path is None or audio_path is None:
                        print('download failed')
                        return
                    print('merging audio and video')
                    self.video_url = util.merge_audio_and_video(audio_path, video_path)
                else:
                    self.video_url = meta_info['video_url']
                video_download_text = '视频下载：<a href=\"' + self.video_url + '\">点此下载</a>'
            self.media_files = [
                {
                    'type': 'video',
                    'url': self.video_url,
                    'caption': ''
                }
            ]
            self.text += video_download_text
        self.content = meta_info['description'].replace('\n', '<br>')

    def get_bilibili_video_info(self, video_info):
        """
        :param video_info: the video info from get_video_info(), which is originally from youtube_dl
        :return: a formatted dict meta_info
        """
        meta_info = {}
        meta_info['id'] = video_info['id']
        meta_info['title'] = video_info['title']
        meta_info['author'] = video_info['uploader']
        meta_info['author_url'] = 'https://space.bilibili.com/' + str(video_info['uploader_id'])
        meta_info['author_avatar'] = video_info['thumbnail']
        meta_info['ext'] = video_info['ext']
        if self.scraper == 'youtube_dl':
            meta_info['description'] = video_info['description'].split(' 视频播放量')[0]
            meta_info['playback_data'] = '视频播放量 ' + util.get_content_between_strings(
                video_info['description'], ' 视频播放量', ', 视频作者')
            meta_info['upload_date'] = video_info['upload_date']
            meta_info['ext'] = video_info['ext']
            meta_info['duration'] = util.second_to_time(round(video_info['duration']))
            meta_info['video_url'] = video_info['formats'][0]['url']
            meta_info['filesize'] = video_info['formats'][0]['filesize']
        elif self.scraper == 'yt_dlp':
            meta_info['description'] = video_info['description']
            meta_info['playback_data'] = '视频播放量：' + str(video_info['view_count']) + \
                                         ' 弹幕数：' + str(video_info['comment_count']) + \
                                         ' 点赞数：' + str(video_info['like_count'])
            meta_info['upload_date'] = util.unix_timestamp_to_utc(video_info['timestamp'])
            meta_info['duration'] = util.second_to_time(round(video_info['duration']))
            if self.hd:
                meta_info['raw_video_content_infos'] = []
                meta_info['audio_content_infos'] = []
                for file_item in video_info['formats']:
                    if file_item['vcodec'] == 'none':
                        meta_info['raw_video_content_infos'].append(file_item)
                    if file_item['acodec'] == 'none':
                        meta_info['audio_content_infos'].append(file_item)
        return meta_info

    def get_youtube_video_info(self, video_info):
        meta_info = {}
        if self.scraper == 'yt_dlp':
            meta_info['id'] = video_info['id']
            meta_info['title'] = video_info['title']
            meta_info['author'] = video_info['uploader']
            meta_info['author_url'] = video_info['uploader_url']
            meta_info['description'] = video_info['description']
            meta_info['playback_data'] = '视频播放量：' + str(video_info['view_count']) + \
                                         ' 点赞数：' + str(video_info['like_count']) + \
                                         ' 评论数：' + str(video_info['comment_count'])
            meta_info['author_avatar'] = video_info['thumbnail']
            meta_info['upload_date'] = str(video_info['upload_date'])
            meta_info['duration'] = util.second_to_time(round(video_info['duration']))
            if not self.hd:
                for i in video_info['formats']:
                    if i['format_id'] == '18':  # 18 is the format id for mp4 360p
                        video_content_info = i
                        break
                meta_info['video_url'] = video_content_info['url']
                meta_info['filesize'] = video_content_info['filesize'] if video_content_info['filesize'] else 0
                meta_info['ext'] = video_content_info['ext']
            if self.hd:
                meta_info['ext'] = video_info['ext']
                meta_info['raw_video_content_infos'] = []
                meta_info['audio_content_infos'] = []
                for file_item in video_info['formats']:
                    if file_item['vcodec'] == 'none':
                        meta_info['raw_video_content_infos'].append(file_item)
                    if file_item['acodec'] == 'none':
                        meta_info['audio_content_infos'].append(file_item)
        return meta_info

    def parse_video_url(self):
        """
        :return: this will directly modify the self object, no return
        """
        # if it's a bilibili url
        if 'bilibili.com' in self.url or 'b23.tv' in self.url:
            self.extractor = 'BiliBili'
            # if the url contains b23.tv, it is a short url, need to expand it
            if 'b23.tv' in self.url:
                response = requests.get(self.url)
                print(response.url)
                self.url = response.url
            if 'm.bilibili.com' in self.url:
                self.url = self.url.replace('m.bilibili.com', 'www.bilibili.com')
            if '/bilibili.com' in self.url:
                self.url = self.url.replace('/bilibili.com', '/www.bilibili.com')
        elif 'youtube.com' in self.url or 'youtu.be' in self.url:
            self.extractor = 'youtube'
            # get the real url
