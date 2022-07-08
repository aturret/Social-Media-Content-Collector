import json
import requests
from collections import OrderedDict
from lxml import etree
import sys
# from . import util
import re
from bs4 import BeautifulSoup



imgpattern = '<.?img[^>]*>'
pattern = re.compile(imgpattern)

# def parse_emoji(str):
#     result = pattern.search(str).group()
#     for i in result:
#         if i.find('alt='):
#             i = re.search(r'(?<=alt=\[).*(?=\])',i)
#         else:
#             i = ""
#     return

class Weibo(object):
    def __init__(self, url):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
            'Cookie': ''}
        self.url = url

    def get_weibo(self, raw=False):
        html = requests.get(self.url, headers=self.headers, verify=False).text
        html = html[html.find('"status":'):]
        print(html)
        print("end")
        html = html[:html.rfind('"hotScheme"')]
        print(html)
        print("end")
        html = html[:html.rfind(',')]
        html = html[:html.rfind('][0] || {};')]
        print(html)
        print("end")
        html = '{' + html
        # html = '{' + html + '}'
        print(html)
        print("end")
        # breakpoint()
        js = json.loads(html, strict=False)
        # print(js)
        weibo_info = js.get('status')
        if weibo_info:
            if not raw:
                weibo = self.parse_weibo(weibo_info)
                print(weibo)
                return weibo
            else:
                return weibo_info

    def get_article_url(self, selector):
        """获取微博中头条文章的url"""
        article_url = ''
        # text = selector.xpath('string(.)')
        # if text.startswith(u'发布了头条文章'):
        url = selector.xpath('//a[.//img/@src="https://h5.sinaimg.cn/upload/2015/09/25/3/timeline_card_small_article_default.png"]/@href')
        if url is not None:
            article_url = url
        return article_url

    def get_pics(self, weibo_info):
        """获取微博原始图片url，以逗号分隔"""
        if weibo_info.get('pics'):
            pic_info = weibo_info['pics']
            pic_list = [pic['large']['url'] for pic in pic_info]
            pics = ','.join(pic_list)
        else:
            pics = ''
        return pics

    def get_pics_new(self, weibo_info):
        """获取微博原始图片url，作为列表"""
        if weibo_info.get('pics'):
            pic_info = weibo_info['pics']
            pic_list = [pic['large']['url'] for pic in pic_info]
            pics = pic_list
        else:
            pics = ''
        return pics

    def get_video_url(self, weibo_info):
        """获取微博视频url"""
        video_url = ''
        video_url_list = []
        if weibo_info.get('page_info'):
            if ((weibo_info['page_info'].get('urls')
                 or weibo_info['page_info'].get('media_info'))
                    and weibo_info['page_info'].get('type') == 'video'):
                media_info = weibo_info['page_info']['urls']
                if not media_info:
                    media_info = weibo_info['page_info']['media_info']
                video_url = media_info.get('mp4_720p_mp4')
                if not video_url:
                    video_url = media_info.get('mp4_hd_url')
                if not video_url:
                    video_url = media_info.get('hevc_mp4_hd')
                if not video_url:
                    video_url = media_info.get('mp4_sd_url')
                if not video_url:
                    video_url = media_info.get('mp4_ld_mp4')
                if not video_url:
                    video_url = media_info.get('stream_url_hd')
                if not video_url:
                    video_url = media_info.get('stream_url')
        if video_url:
            video_url_list.append(video_url)
        live_photo_list = self.get_live_photo(weibo_info)
        if live_photo_list:
            video_url_list += live_photo_list
        return ';'.join(video_url_list)

    def get_live_photo(self, weibo_info):
        """获取live photo中的视频url"""
        live_photo_list = []
        live_photo = weibo_info.get('pic_video')
        if live_photo:
            prefix = 'https://video.weibo.com/media/play?livephoto=//us.sinaimg.cn/'
            for i in live_photo.split(','):
                if len(i.split(':')) == 2:
                    url = prefix + i.split(':')[1] + '.mov'
                    live_photo_list.append(url)
            return live_photo_list

    def get_location(self, selector):
        """获取微博发布位置"""
        location_icon = 'timeline_card_small_location_default.png'
        span_list = selector.xpath('//span')
        location = ''
        for i, span in enumerate(span_list):
            if span.xpath('img/@src'):
                if location_icon in span.xpath('img/@src')[0]:
                    location = span_list[i + 1].xpath('string(.)')
                    break
        return location

    def standardize_info(self, weibo):
        for k, v in weibo.items():
            if 'bool' not in str(type(v)) and 'int' not in str(
                    type(v)) and 'list' not in str(
                type(v)) and 'long' not in str(type(v)):
                weibo[k] = v.replace(u'\u200b', '').encode(
                    sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding)
        return weibo

    def string_to_int(self, string):
        """字符串转换为整数"""
        if isinstance(string, int):
            return string
        elif string.endswith(u'万+'):
            string = string[:-2] + '0000'
        elif string.endswith(u'万'):
            string = float(string[:-1]) * 10000
        elif string.endswith(u'亿'):
            string = float(string[:-1]) * 100000000
        return int(string)

    def get_topics(self, selector):
        """获取参与的微博话题"""
        span_list = selector.xpath("//span[@class='surl-text']")
        topics = ''
        topic_list = []
        for span in span_list:
            text = span.xpath('string(.)')
            if len(text) > 2 and text[0] == '#' and text[-1] == '#':
                topic_list.append(text[1:-1])
        if topic_list:
            topics = ','.join(topic_list)
        return topics

    def get_at_users(self, selector):
        """获取@用户"""
        a_list = selector.xpath('//a')
        at_users = ''
        at_list = []
        for a in a_list:
            if '@' + a.xpath('@href')[0][3:] == a.xpath('string(.)'):
                at_list.append(a.xpath('string(.)')[1:])
        if at_list:
            at_users = ','.join(at_list)
        return at_users

    def parse_date(self, weibo_info):
        zday = '星期识别错误'
        zmonth = '月份识别错误'
        parse = weibo_info['created_at'].split()
        day = parse[0]
        if day == 'Mon':
            zday = '星期一'
        elif day == 'Tue':
            zday = '星期二'
        elif day == 'Wed':
            zday = '星期三'
        elif day == 'Thu':
            zday = '星期四'
        elif day == 'Fri':
            zday = '星期五'
        elif day == 'Sat':
            zday = '星期六'
        elif day == 'Sun':
            zday = '星期日'
        month = parse[1]
        if month == 'Jan':
            zmonth = '1'
        elif month == 'Feb':
            zmonth = '2'
        elif month == 'Mar':
            zmonth = '3'
        elif month == 'Apr':
            zmonth = '4'
        elif month == 'May':
            zmonth = '5'
        elif month == 'Jun':
            zmonth = '6'
        elif month == 'Jul':
            zmonth = '7'
        elif month == 'Aug':
            zmonth = '8'
        elif month == 'Sep':
            zmonth = '9'
        elif month == 'Oct':
            zmonth = '10'
        elif month == 'Nov':
            zmonth = '11'
        elif month == 'Dec':
            zmonth = '12'
        date = parse[2]
        time = parse[3]
        year = parse[5]
        text = '发表于'+year+'年'+zmonth+'月'+date+'日('+zday+') '+time
        return text

    def parse_weibo(self, weibo_info):
        weibo = OrderedDict()
        if weibo_info['user']:
            weibo['user_id'] = weibo_info['user']['id']
            weibo['screen_name'] = weibo_info['user']['screen_name']
        else:
            weibo['user_id'] = ''
            weibo['screen_name'] = ''
        weibo['id'] = int(weibo_info['id'])
        weibo['bid'] = weibo_info['bid']
        text_body = weibo_info['text']
        selector = etree.HTML(text_body)
        # weibo['text'] = re.sub(pattern, "", text_body)
        # weibo['text'] = selector.xpath('string(.)')
        weibo['text'] = text_body.replace('<br />', '<br>')
        weibo['article_url'] = self.get_article_url(selector)
        weibo['pics'] = self.get_pics(weibo_info)
        weibo['pics_new'] = self.get_pics_new(weibo_info)
        weibo['video_url'] = self.get_video_url(weibo_info)
        weibo['location'] = self.get_location(selector)
        weibo['created_at'] = weibo_info['created_at']
        weibo['source'] = weibo_info['source']
        weibo['attitudes_count'] = self.string_to_int(
            weibo_info.get('attitudes_count', 0))
        weibo['comments_count'] = self.string_to_int(
            weibo_info.get('comments_count', 0))
        weibo['reposts_count'] = self.string_to_int(
            weibo_info.get('reposts_count', 0))
        weibo['topics'] = self.get_topics(selector)
        weibo['at_users'] = self.get_at_users(selector)
        # 处理图片和视频
        picsformat = ''
        videoformat = ''
        if weibo['pics_new'] != '':
            piclist = weibo['pics_new']
            for i in piclist:
                picsformat += '<img src="' + i + '"><br />'
                # print(picsformat)
        if weibo['video_url'] != '':
            videoformat = '<video><source src="' + weibo['video_url'] + '" type="video/mp4">youcannotwatchthevideo</video>'
        #处理头条文章
        # if weibo['article_url'] != '':
            # aurl=weibo['article_url']
            # aurl.replace('weibo.com','m.weibo.cn')
        weibo['title'] = weibo['screen_name'] + '的微博'
        weibo['origin'] = weibo['screen_name']
        weibo['aurl'] = self.url
        weibo['originurl'] = 'https://weibo.com/u/' + str(weibo['user_id'])
        weibo['date'] = self.parse_date(weibo_info)
        weibo['count'] = '转发：'+str(weibo_info['reposts_count'])+' 评论：'+str(weibo_info['comments_count'])+' 点赞：'+str(weibo_info['attitudes_count'])
        weibo['content'] = '<br><p>'+weibo['date']+'</p><br><p>'+weibo['count']+'</p><br><a href="'+weibo['originurl'] +'">@'+ weibo['origin'] +'</a>：<p>'+ weibo['text'] +'</p><br>' + picsformat + videoformat
        if 'retweeted_status' in weibo_info:
            rtweibo_url='https://m.weibo.cn/status/'+weibo_info['retweeted_status']['id']
            weibo['rturl']=rtweibo_url
            rtweibo=Weibo(rtweibo_url)
            rtweibo_info=rtweibo.get_weibo()
            # rtweibo_info['content'] = '<a href="'+ rtweibo_info['originurl'] + '">@' + rtweibo_info['screen_name'] + '：</a>' + rtweibo_info['content']
            weibo['content'] += '<br><hr>' + rtweibo_info['content']
        else:
            weibo['rturl']=''
        print(weibo['content'])
        # print(weibo)
        return self.standardize_info(weibo)

### TEST CODE ###

# testurl='https://m.weibo.cn/1989660417/yp2eLrUhm'
# testurl='https://m.weibo.cn/7605038522/LBlABpi7K'
# testurl='https://m.weibo.cn/7755701767/LqLOSvqP3'
#
# wb = Weibo(testurl)
# wb.get_weibo()