import re
import yt_dlp
import youtube_dl
from app.utils import util


class VideoConverter(object):
    def __init__(self, url, **kwargs):
        self.url = url
        self.aurl = url
        self.ydl_opts = {
            'format': 'best',
            # 'format': 'best/bestvideo+bestaudio',
        }
        self.scraper = kwargs.get('scraper', 'youtube_dl')
        self.download = kwargs.get('download', True)
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
                video_info = ydl.extract_info(self.url, download=False)
        elif self.scraper == 'yt_dlp':
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                video_info = ydl.extract_info(self.url, download=False, process=False)
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
        self.video_url = meta_info['video_url']
        self.text = \
            '<a href=\"' + self.url + '\"><b>' + self.title + '</b></a>\n' + \
            '作者：<a href=\"' + self.originurl + '\">' + self.origin + '</a>\n' + \
            '视频时长：' + self.duration + '\n' + \
            '视频上传日期：' + self.created + '\n' + \
            '播放数据：' + meta_info['playback_data'] + '\n' + \
            '视频简介：' + meta_info['description'] + '\n'
        if self.download:
            # if meta_info['filesize'] > 50000000:
            #     print('filesize too large, cannot upload to telegram')
            #     video_download_text = '视频文件过大，无法上传到 Telegram，请点击链接下载：<a href=\"' + self.video_url + '\">点此下载</a>'
            # else:
            self.media_files = [
                {
                    'type': 'video',
                    'url': self.video_url,
                    'caption': ''
                }
            ]
            video_download_text = '视频下载：<a href=\"' + self.video_url + '\">点此下载</a>'
            # video_download_text = '视频提取成功，也可以前往 <a href=\"' + self.video_url + '\">下载</a>'
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
            meta_info['description'] = video_info['description'].split(', 视频播放量')[0]
            meta_info['playback_data'] = '视频播放量 ' + util.get_content_between_strings(
                video_info['description'], ', 视频播放量', ', 视频作者')
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
            for i in video_info['formats']:
                if i['format_id'] == '18':  # 18 is the format id for mp4 360p
                    video_content_info = i
                    break
            if video_content_info:
                meta_info['video_url'] = video_content_info['url']
                meta_info['filesize'] = video_content_info['filesize'] if video_content_info['filesize'] else 0
                meta_info['ext'] = video_content_info['ext']
        return meta_info
