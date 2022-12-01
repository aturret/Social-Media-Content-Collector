import hashlib
from html_telegraph_poster import TelegraphPoster
import json
import traceback
# import logging
import sys
import time
import requests
from lxml import etree
from html_sanitizer import Sanitizer
from . import settings

# Set GENERATE_TEST_DATA to True when generating test data.
GENERATE_TEST_DATA = False
TEST_DATA_DIR = 'tests/testdata'
URL_MAP_FILE = 'url_map.json'
DOWNLOAD_DIR = settings.env_var.get('DOWNLOAD_DIR',
                                    settings.env_var.get('HOMEPATH' if settings.system == 'Windows' else 'HOME', '~'))
print(DOWNLOAD_DIR)

# logger = logging.getLogger('spider.util')

wsanitizer = Sanitizer({
    "tags": {
        "a", "h1", "h2", "h3", "strong", "em", "p", "ul", "ol",
        "li", "br", "sub", "sup", "hr",
    },
    "attributes": {"a": ("href", "name", "target", "title", "id", "rel")},
    "empty": {"hr", "a", "br"},
    "separate": {"a", "p", "li"},
    "whitespace": {"br"},
    "keep_typographic_whitespace": False,
    "add_nofollow": False,
    "autolink": False,
    # "sanitize_href": sanitize_href,
    "element_postprocessors": [],
})


def get_selector(url, headers):
    html = requests.get(url=url, headers=headers).text
    selector = etree.HTML(html)
    return selector


def local_time():
    time1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(round(time.time() * 1000)) / 1000))
    return time1


def hash_url(url):
    return hashlib.sha224(url.encode('utf8')).hexdigest()


def handle_html(url):
    """处理html"""
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
        headers = {'User_Agent': user_agent}
        # headers = {'User_Agent': user_agent, 'Cookie': cookie}
        resp = requests.get(url, headers=headers)

        if GENERATE_TEST_DATA:
            import io
            import os

            resp_file = os.path.join(TEST_DATA_DIR, '%s.html' % hash_url(url))
            with io.open(resp_file, 'w', encoding='utf-8') as f:
                f.write(resp.text)

            with io.open(os.path.join(TEST_DATA_DIR, URL_MAP_FILE), 'r+') as f:
                url_map = json.loads(f.read())
                url_map[url] = resp_file
                f.seek(0)
                f.write(json.dumps(url_map, indent=4, ensure_ascii=False))
                f.truncate()

        selector = etree.HTML(resp.content)
        return selector
    except Exception as e:
        return "1"
        # logger.exception(e)


def handle_garbled(info):
    """处理乱码"""
    try:
        info = (info.xpath('string(.)').replace(u'\u200b', '').encode(
            sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding))
        return info
    except Exception as e:
        # logger.exception(e)
        return u'无'


def bid2mid(bid):
    """convert string bid to string mid"""
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    base = len(alphabet)
    bidlen = len(bid)
    head = bidlen % 4
    digit = int((bidlen - head) / 4)
    dlist = [bid[0:head]]
    for d in range(1, digit + 1):
        dlist.append(bid[head:head + d * 4])
        head += 4
    mid = ''
    for d in dlist:
        num = 0
        idx = 0
        strlen = len(d)
        for char in d:
            power = (strlen - (idx + 1))
            num += alphabet.index(char) * (base ** power)
            idx += 1
            strnum = str(num)
            while (len(d) == 4 and len(strnum) < 7):
                strnum = '0' + strnum
        mid += strnum
    return mid


def to_video_download_url(cookie, video_page_url):
    if video_page_url == '':
        return ''

    video_object_url = video_page_url.replace('m.weibo.cn/s/video/show',
                                              'm.weibo.cn/s/video/object')
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
        headers = {'User_Agent': user_agent, 'Cookie': cookie}
        wb_info = requests.get(video_object_url, headers=headers).json()
        video_url = wb_info['data']['object']['stream'].get('hd_url')
        if not video_url:
            video_url = wb_info['data']['object']['stream']['url']
            if not video_url:  # This video is a live 说明该视频为直播
                video_url = ''
    except json.decoder.JSONDecodeError:
        return "1"
        # logger.warning(u'当前账号没有浏览该视频的权限')

    return video_url


def string_to_int(string):
    """字符串转换为整数"""
    '''transfer Chinese character numeric string to int'''
    if isinstance(string, int):
        return string
    elif string.endswith(u'万+'):
        string = string[:-2] + '0000'
    elif string.endswith(u'万'):
        string = float(string[:-1]) * 10000
    elif string.endswith(u'亿'):
        string = float(string[:-1]) * 100000000
    return int(string)


def download_file(format: set = ('html')):
    return '1'


def telegraph_convert(tdict):
    res = ''
    try:
        metadata_dict = tdict

        # url = 'https://'+cfg['huginn']['url']+'/users/2/web_requests/'+cfg['huginn']['webrequest']['telegraph']
        # definite the keys of the json file
        author = 'origin'
        author_url = 'originurl'
        # metadata_dict = content_data
        print('type of argument:' + str(type(metadata_dict)))
        print('content of argument:' + str(metadata_dict))
        # Use pyhtmltotelegraph to post telegraph article

        t = TelegraphPoster(use_api=True)
        short_name = metadata_dict[author]
        t.create_api_token(short_name[0:14], author_name=metadata_dict[author])
        telegraphPost = t.post(title=metadata_dict['title'], author=metadata_dict[author],
                               text=metadata_dict['content'], author_url=metadata_dict[author_url])
        print('telegraph url:' + telegraphPost['url'])
        print('telegraph result type:' + str(type(telegraphPost)))
        res = telegraphPost['url']
    except Exception:
        print(traceback.format_exc())
    # check if the title is a duplicate

    return res if res else 'nothing'
