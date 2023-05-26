import re
import yt_dlp
from app.utils import util


class VideoConverter(object):
    def __init__(self, url):
        self.url = url
        self.aurl = url
        self.ydl_opts = {
            # 'format': 'best/bestvideo+bestaudio',
        }

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
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            video_info = ydl.extract_info(self.url, download=False, process=False)
            print(video_info)
            return video_info

    def video_info_formatting(self, video_info):
        if video_info['extractor'] == 'BiliBili':
            self.category = 'Bilibili'
            meta_info = self.get_bilibili_video_info(video_info)
        elif video_info['extractor'] == 'YouTube':
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
        self.video_url = meta_info['video_url']
        if meta_info['filesize'] > 50000000:
            print('filesize too large, cannot upload to telegram')
            video_download_text = '视频文件过大，无法上传到 Telegram，请点击链接下载：<a href=\"' + self.video_url + '\">点此下载</a>'
        else:
            self.media_files = [
                {
                    'type': 'video',
                    'url': self.video_url,
                    'caption': ''
                }
            ]
            video_download_text = '视频提取成功'
        self.text = \
            '<a href=\"' + self.url + '\"><b>' + self.title + '</b></a>\n' + \
            '作者：<a href=\"' + self.originurl + '\">' + self.origin + '</a>\n' + \
            '播放数据：' + meta_info['playback_data'] + '\n' + \
            '视频简介：' + meta_info['description'] + '\n' + \
            video_download_text
        self.content = meta_info['description']

    def get_bilibili_video_info(self, video_info):
        meta_info = {}
        meta_info['title'] = video_info['title']
        meta_info['author'] = video_info['uploader']
        meta_info['author_url'] = 'https://space.bilibili.com/' + video_info['uploader_id']
        meta_info['description'] = video_info['description'].split(', 视频播放量')[0]
        meta_info['playback_data'] = '视频播放量 ' + util.get_content_between_strings(
            video_info['description'], ', 视频播放量', ', 视频作者')
        meta_info['author_avatar'] = video_info['thumbnail']
        meta_info['upload_date'] = video_info['upload_date']
        meta_info['ext'] = video_info['ext']
        meta_info['duration'] = util.second_to_time(round(video_info['duration']))
        meta_info['video_url'] = video_info['formats'][0]['url']
        meta_info['filesize'] = video_info['formats'][0]['filesize']
        return meta_info

    def get_youtube_video_info(self, video_info):
        meta_info = {}
        meta_info['title'] = video_info['title']
        meta_info['author'] = video_info['uploader']
        meta_info['description'] = video_info['description']
        return meta_info
