import re
import requests
import tempfile
import yt_dlp
import youtube_dl
from app.settings import env_var
from app.utils import util

TEMP_DIR = env_var.get('TEMP_DIR', tempfile.gettempdir())


class VideoConverter(object):
    def __init__(self, url, **kwargs):
        self.url = url
        self.parse_video_url()
        self.aurl = self.url
        self.ydl_opts = {
            'format': 'best',
            'paths': {
                'home': TEMP_DIR
            },
            # 'format': 'best/bestvideo+bestaudio',
        }
        self.scraper = kwargs.get('scraper', 'youtube_dl')
        self.download = kwargs.get('download', True)
        self.hd = kwargs.get('hd', False)
        self.type = 'short'
        if self.hd:
            self.scraper = 'yt_dlp'

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
        download = False
        if self.scraper == 'youtube_dl':
            with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                video_info = ydl.extract_info(self.url, download=download)
        elif self.scraper == 'yt_dlp':
            if self.hd and self.extractor == 'youtube':
                self.ydl_opts['format'] = 'bestvideo[ext=webm]+251/bestvideo[ext=mp4]+(258/256/140)/bestvideo[ext=webm]+(250/249)/best'
                download = True
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                video_info = ydl.extract_info(self.url, download=download, process=False)
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
        self.type = 'long' if len(meta_info['description']) > 500 else 'short'
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
            if self.hd:
                print('download hd video, this may take a while')
                video_path = util.download_file(meta_info['raw_video_url'], extension=meta_info['raw_video_ext'])
                audio_path = util.download_file(meta_info['audio_url'], extension=meta_info['audio_ext'])
                print('merging audio and video')
                self.video_url = util.merge_audio_and_video(audio_path, video_path)
            else:
                self.video_url = meta_info['video_url']
            self.media_files = [
                {
                    'type': 'video',
                    'url': self.video_url,
                    'caption': ''
                }
            ]
            video_download_text = '视频下载：<a href=\"' + self.video_url + '\">点此下载</a>'
            self.text += video_download_text
        self.content = meta_info['description'].replace('\n', '<br>')

    def get_bilibili_video_info(self, video_info):
        """
        :param video_info: the video info from get_video_info(), which is originally from youtube_dl
        :return: a formatted dict meta_info
        """
        meta_info = {}
        if self.scraper == 'youtube_dl':
            meta_info['title'] = video_info['title']
            meta_info['author'] = video_info['uploader']
            meta_info['author_url'] = 'https://space.bilibili.com/' + video_info['uploader_id']
            meta_info['description'] = video_info['description'].split(' 视频播放量')[0]
            meta_info['playback_data'] = '视频播放量 ' + util.get_content_between_strings(
                video_info['description'], ' 视频播放量', ', 视频作者')
            meta_info['author_avatar'] = video_info['thumbnail']
            meta_info['upload_date'] = video_info['upload_date']
            meta_info['ext'] = video_info['ext']
            meta_info['duration'] = util.second_to_time(round(video_info['duration']))
            meta_info['video_url'] = video_info['formats'][0]['url']
            meta_info['filesize'] = video_info['formats'][0]['filesize']
        # elif self.scraper == 'yt_dlp':

        return meta_info

    def get_youtube_video_info(self, video_info):
        meta_info = {}
        if self.scraper == 'yt_dlp':
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
                for i in video_info['formats']:
                    if i['format_id'] == '137':  # 137 is the format id for mp4 1080p
                        raw_video_content_info = i
                    if i['format_id'] == '140':  # 140 is the format id for mp4 audio
                        audio_content_info = i
                meta_info['raw_video_url'] = raw_video_content_info['url']
                meta_info['raw_video_filesize'] = raw_video_content_info['filesize'] if raw_video_content_info['filesize'] else 0
                meta_info['raw_video_ext'] = raw_video_content_info['ext']
                meta_info['audio_url'] = audio_content_info['url']
                meta_info['audio_filesize'] = audio_content_info['filesize'] if audio_content_info['filesize'] else 0
                meta_info['audio_ext'] = audio_content_info['ext']
        return meta_info

    def parse_video_url(self):
        """
        :return: this will directly modify the self object, no return
        """
        # if it's a bilibili url
        if 'bilibili.com' in self.url or 'b23.tv' in self.url:
        # if the url contains b23.tv, it is a short url, need to expand it
            if 'b23.tv' in self.url:
                response = requests.get(self.url)
                print(response.url)
                self.url = response.url
            self.extractor = 'BiliBili'
        elif 'youtube.com' in self.url or 'youtu.be' in self.url:
            self.extractor = 'youtube'
            # get the real url