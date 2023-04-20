import json
import requests
from collections import OrderedDict
from lxml import etree
from lxml import html
from app import settings
import sys
import re
from bs4 import BeautifulSoup
from app.utils.util import get_response_json
from app.utils.util import get_html_text_length

imgpattern = '<.?img[^>]*>'
pattern = re.compile(imgpattern)
ajax_host = 'https://weibo.com/ajax/statuses/show?id='
ajax_host_longtext = 'https://weibo.com/ajax/statuses/longtext?id='
short_limit = settings.env_var.get('SHORT_LIMIT', 200)
weibo_cookie = settings.env_var.get('WEIBO_COOKIE', '')
cookie_mode = settings.env_var.get('COOKIE_MODE', 'False')


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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'Cookie': weibo_cookie if weibo_cookie else '', }
        self.url = url
        self.status_id = url.split('/')[-1]
        self.ajax_url = ajax_host + self.status_id
        self.longtext_url = ajax_host_longtext + self.status_id
        self.isLongText = False
        self.type = 'long'

    def get_weibo(self, raw=False):
        html = requests.get(self.url, headers=self.headers, verify=False).text
        html = html[html.find('"status":'):]
        # print(html)
        # print("end")
        html = html[:html.rfind('"hotScheme"')]
        # print(html)
        # print("end")
        html = html[:html.rfind(',')]
        html = html[:html.rfind('][0] || {};')]
        # print(html)
        # print("end")
        html = '{' + html
        # html = '{' + html + '}'

        # print("end")
        # breakpoint()
        js = json.loads(html, strict=False)
        # print(js)
        weibo_info = js.get('status')
        if weibo_info:
            if not raw:
                weibo = self.parse_weibo(weibo_info)
                # print(weibo)
                print(html)
                return weibo
            else:
                return weibo_info

    def get_weibo_info_old(self):
        old_weibo_url = 'http://m.weibo.cn/status/' + self.status_id
        # print(old_weibo_url)
        html = requests.get(old_weibo_url, headers=self.headers, verify=False).text
        html = html[html.find('"status":'):]
        html = html[:html.rfind('"hotScheme"')]
        html = html[:html.rfind(',')]
        html = html[:html.rfind('][0] || {};')]
        html = '{' + html
        # print(html)
        js = json.loads(html, strict=False)
        weibo_info = js.get('status')
        return weibo_info

    def get_article_url(self, selector):
        article_url = ''
        url = selector.xpath(
            '//a[.//img/@src="https://h5.sinaimg.cn/upload/2015/09/25/3/timeline_card_small_article_default.png"]/@href')
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
        elif 'pic_infos' in weibo_info and weibo_info.get('pic_num') > 0:
            pic_info = weibo_info['pic_infos']
            pic_list = []
            for pic in pic_info:
                pic_list.append(pic_info[pic]['original']['url']) if pic_info[pic]['original'] else \
                    pic_list.append(pic_info[pic]['large']['url'])
            pics = pic_list
        elif 'mix_media_info' in weibo_info:
            pic_list = []
            for item in weibo_info['mix_media_info']['items']:
                if item['type'] == 'pic':
                    pic_list.append(item['data']['original']['url']) if item['data']['original'] else \
                        pic_list.append(item['data']['large']['url'])
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
                    and (weibo_info['page_info'].get('type') == 'video'
                         or weibo_info['page_info'].get('object_type') == 'video')):
                media_info = weibo_info['page_info']['urls'] if weibo_info['page_info'].get('urls') else ''
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
                video_url_list.append(video_url)
        elif weibo_info.get('mix_media_info'):
            for items in weibo_info['mix_media_info']['items']:
                if items.get('type') == 'video':
                    video_url = items.get('stream_url_hd')
                    if not video_url:
                        video_url = items['data']['media_info'].get('mp4_720p_mp4')
                    if not video_url:
                        video_url = items['data']['media_info'].get('mp4_hd_url')
                    if not video_url:
                        video_url = items['data']['media_info'].get('hevc_mp4_hd')
                    if not video_url:
                        video_url = items['data']['media_info'].get('mp4_sd_url')
                    if not video_url:
                        video_url = items['data']['media_info'].get('mp4_ld_mp4')
                    if not video_url:
                        video_url = items['data']['media_info'].get('stream_url_hd')
                    if not video_url:
                        video_url = items['data']['media_info'].get('stream_url')
                    video_url_list.append(video_url)
        live_photo_list = self.get_live_photo(weibo_info)
        if live_photo_list:
            video_url_list += live_photo_list
        return video_url_list

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
        daydict = {'Mon': '星期一', 'Tue': '星期二', 'Wed': '星期三', 'Thu': '星期四', 'Fri': '星期五', 'Sat': '星期六', 'Sun': '星期日'}
        zday = daydict[day]
        month = parse[1]
        monthdict = {'Jan': '1', 'Feb': '2', 'Mar': '3', 'Apr': '4', 'May': '5', 'Jun': '6', 'Jul': '7', 'Aug': '8',
                        'Sep': '9', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
        zmonth = monthdict[month]
        date = int(parse[2])
        time = parse[3]
        year = parse[5]
        text = '发布于' + year + '年' + zmonth + '月' + str(date) + '日(' + zday + ') ' + time + '<br>通过' + \
               weibo_info['source'] + '发布'
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
        weibo['text'] = text_body.replace('<br />', '<br>').replace('br/', 'br')
        print(weibo['text'])
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
        if weibo['video_url'] != '':
            for i in weibo['video_url']:
                videoformat += '<video><source src="' + i + '" type="video/mp4">youcannotwatchthevideo</video>'
        weibo['title'] = weibo['screen_name'] + '的微博'
        weibo['origin'] = weibo['screen_name']
        weibo['aurl'] = self.url
        weibo['originurl'] = 'https://weibo.com/u/' + str(weibo['user_id'])
        weibo['date'] = self.parse_date(weibo_info)
        weibo['count'] = '转发:' + str(weibo_info['reposts_count']) + ' 评论:' + str(
            weibo_info['comments_count']) + ' 点赞:' + str(weibo_info['attitudes_count'])
        weibo['content'] = '<br><p>' + weibo['date'] + '</p><br><p>' + weibo['count'] + '</p><br><a href="' + weibo[
            'originurl'] + '">@' + weibo['origin'] + '</a>：<p>' + weibo['text'] + '</p><br>' + picsformat + videoformat
        if 'retweeted_status' in weibo_info:
            rtweibo_url = 'https://m.weibo.cn/status/' + weibo_info['retweeted_status']['id']
            weibo['rturl'] = rtweibo_url
            rtweibo = Weibo(rtweibo_url)
            rtweibo_info = rtweibo.get_weibo()
            # rtweibo_info['content'] = '<a href="'+ rtweibo_info['originurl'] + '">@' + rtweibo_info['screen_name'] + '：</a>' + rtweibo_info['content']
            weibo['content'] += '<br><hr>' + rtweibo_info['content']
        else:
            weibo['rturl'] = ''
        # print(weibo['content'])
        # print(weibo)
        return self.standardize_info(weibo)

    def new_get_weibo(self):
        url = self.ajax_url.replace('m.weibo.cn', 'weibo.com')
        ajax_json = get_response_json(url, headers=self.headers)
        print('ajax_json file url: ' + url)
        if ajax_json['ok'] == 0:
            return None
        weibo = self.new_parse_weibo(ajax_json)
        return weibo

    def new_parse_weibo(self, weibo_info):
        weibo = OrderedDict()
        if weibo_info['user']:
            weibo['user_id'] = weibo_info['user']['id']
            weibo['screen_name'] = weibo_info['user']['screen_name']
        else:
            weibo['user_id'] = 'Unknown user id'
            weibo['screen_name'] = 'Unknown name'
        weibo['id'] = int(weibo_info['id'])
        # non-long text weibo
        if not weibo_info['isLongText'] or (weibo_info['pic_num'] > 9 and weibo_info['isLongText']):
            cleaned_text, fw_pics = self.weibo_html_text_clean(weibo_info['text'])
            print('cleaned weibo text:\n' + cleaned_text)
            weibo['text'] = cleaned_text.replace('<br />', '<br>').replace('br/', 'br')
        # long-text weibo
        else:
            self.type = 'long'
            # if we have cookie to get long text from ajax request
            if self.headers['Cookie'] and cookie_mode == 'True':
                longtext_json = get_response_json(self.longtext_url, headers=self.headers)
                weibo['text'] = weibo['text_raw'] = longtext_json['data']['longTextContent']
                weibo['text'] = weibo['text'].replace('\n', '<br>')
            # scrape long text from old method (http://m.weibo.cn)
            else:
                temp_info = self.get_weibo_info_old()
                cleaned_text, fw_pics = self.weibo_html_text_clean(temp_info['text'])
                weibo['text'] = cleaned_text.replace('<br />', '<br>').replace('br/', 'br')

        print('weibo text:\n' + weibo['text'])
        # weibo['article_url'] = self.get_article_url(selector)
        # weibo['pics'] = self.get_pics(weibo_info)
        weibo['pics_new'] = self.get_pics_new(weibo_info)
        weibo['video_url'] = self.get_video_url(weibo_info)
        # weibo['location'] = self.get_location(selector)
        weibo['created_at'] = weibo_info['created_at']
        weibo['source'] = weibo_info['source']
        weibo['attitudes_count'] = self.string_to_int(
            weibo_info.get('attitudes_count', 0))
        weibo['comments_count'] = self.string_to_int(
            weibo_info.get('comments_count', 0))
        weibo['reposts_count'] = self.string_to_int(
            weibo_info.get('reposts_count', 0))
        # weibo['topics'] = self.get_topics(selector)
        # weibo['at_users'] = self.get_at_users(selector)
        # 处理图片和视频
        pics_format = ''
        video_format = ''
        if weibo['pics_new']:
            if not weibo_info['isLongText'] and len(fw_pics) > 0:
                pic_list = fw_pics.extend(weibo['pics_new'])
            else:
                pic_list = weibo['pics_new']
            for i in pic_list:
                pics_format += '<img src="' + i + '"><br>'
        if weibo['video_url']:
            for i in weibo['video_url']:
                video_format += '<video><source src="' + i + '" type="video/mp4">youcannotwatchthevideo</video>'
        weibo['title'] = weibo['screen_name'] + '的微博'
        weibo['origin'] = weibo['screen_name']
        weibo['aurl'] = self.url
        weibo['originurl'] = 'https://weibo.com/u/' + str(weibo['user_id'])
        weibo['date'] = self.parse_date(weibo_info)
        weibo['count'] = '转发:' + str(weibo_info['reposts_count']) + ' 评论:' + str(
            weibo_info['comments_count']) + ' 点赞:' + str(weibo_info['attitudes_count'])
        weibo['region_name'] = weibo_info['region_name'] if 'region_name' in weibo_info else ''
        weibo['content'] = '<br><p>' + weibo['date'] + '</p><br><p>' + \
                           weibo['count'] + ' ' + weibo['region_name'] + \
                           '</p><br><a href="' + weibo['originurl'] + '">@' + weibo['origin'] + \
                           '</a>：<p>' + weibo['text'] + '</p><br>' + pics_format + video_format

        weibo['media_files'] = []
        for i in weibo['pics_new']:
            item = {'type': 'image', 'url': i, 'caption': ''}
            weibo['media_files'].append(item)
        for i in weibo['video_url']:
            item = {'type': 'video', 'url': i, 'caption': ''}
            weibo['media_files'].append(item)
        # get retweeted weibo
        if 'retweeted_status' in weibo_info:
            rtweibo_url = 'https://weibo.com/status/' + str(weibo_info['retweeted_status']['id'])
            weibo['rturl'] = rtweibo_url
            rtweibo = Weibo(rtweibo_url)
            rtweibo_info = rtweibo.new_get_weibo()
            weibo['content'] += '<br><hr>' + rtweibo_info['content']
            weibo['media_files'].extend(rtweibo_info['media_files']) if rtweibo_info['media_files'] else ''
        else:
            weibo['rturl'] = ''
        # combine text with original weibo
        weibo['text_raw'] = weibo_info['text_raw'] + rtweibo_info['text_raw'] if 'retweeted_status' in weibo_info \
            else weibo_info['text_raw']
        print('length of raw text:' + str(len(weibo['text_raw'])))
        # check the type of combined weibo

        self.type = 'long' if get_html_text_length(weibo['text']) > short_limit else 'short'
        weibo['text'] = '<a href="' + weibo['aurl'] + '">@' + weibo['origin'] + \
                        '</a>：' + weibo['text'].replace('<br>', '\n')
        weibo['text'] = weibo['text'] + ('\n' + rtweibo_info['text']) if 'retweeted_status' in weibo_info \
            else weibo['text']
        weibo['text'] = weibo['text'].replace('href="//', 'href="https://')
        weibo['type'] = self.type
        return self.standardize_info(weibo)

    def weibo_html_text_clean(self, text, method='bs4'):
        fw_pics = []
        if method == 'bs4':
            soup = BeautifulSoup(text, 'html.parser')
            for img in soup.find_all('img'):
                alt_text = img.get('alt', '')
                img.replace_with(alt_text)
            for a in soup.find_all('a'):
                if a.text == '查看图片':
                    fw_pics.append(a.get('href'))
                if '/n/' in a.get('href') and a.get('usercard'):
                    a['href'] = 'https://weibo.com' + a.get('href')
            if self.type == 'long':
                # telegra.ph doesn't support span tag
                for i in soup.find_all('span'):
                    i.decompose()
            res = str(soup).replace('href="//', 'href="http://').replace('href="/n/', 'href="http://weibo.com/n/')
            return res, fw_pics

        if method == 'lxml':
            selector = html.fromstring(text)
            # remove all img tags and replace with alt text
            for img in selector.xpath('//img'):
                alt_text = img.get('alt', '')
                # get innerhtml pure text of the parent tag
                parent_text = img.getparent().text_content() if img.getparent() else ''
                replace_text = alt_text + parent_text
                text_node = html.fromstring(replace_text)
                img.addprevious(text_node)
                img.getparent().remove(img)
                # make text_node become pure text
                text_node.text = text_node.text_content()
            # return the html document after cleaning
            return html.tostring(selector, encoding='unicode')
