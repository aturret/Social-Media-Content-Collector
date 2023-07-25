import traceback
from html_telegraph_poster import TelegraphPoster
from html_telegraph_poster.utils import DocumentPreprocessor
from .converter import weibo, twitter, douban, zhihu, mustodon, instagram, videos, threads
from bs4 import BeautifulSoup
from .utils import util
from .utils.customized_errors import *


class TelegraphDict(object):
    def __init__(self, dict_data: dict, **kwargs):
        self.title = dict_data['title'] if 'title' in dict_data \
            else kwargs['title'] if 'title' in kwargs \
            else 'undefined_title'
        self.content = dict_data['content'] if 'content' in dict_data \
            else kwargs['content'] if 'content' in kwargs \
            else 'undefined_content'
        self.author = dict_data['author'] if 'author' in dict_data \
            else kwargs['author'] if 'author' in kwargs \
            else 'undefined_origin'
        self.author_url = dict_data['author_url'] if 'author_url' in dict_data \
            else kwargs['author_url'] if 'author_url' in kwargs \
            else 'undefined_author_url'
        self.url = dict_data['aurl'] if 'aurl' in dict_data \
            else kwargs['aurl'] if 'aurl' in kwargs \
            else 'undefined_url'

    def to_dict(self):
        return {
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'author_url': self.author_url,
            'url': self.url
        }


class MetadataDict(object):
    def __init__(self, dict_data: dict, **kwargs):
        self.category = dict_data['category'] if 'category' in dict_data \
            else kwargs['category'] if 'category' in kwargs \
            else 'undefined_category'
        self.title = dict_data['title'] if 'title' in dict_data \
            else kwargs['title'] if 'title' in kwargs \
            else 'undefined_title'
        self.text = dict_data['text'] if 'text' in dict_data \
            else kwargs['text'] if 'text' in kwargs \
            else ''
        self.author = dict_data['author'] if 'author' in dict_data \
            else kwargs['author'] if 'author' in kwargs \
            else 'undefined_origin'
        self.author_url = dict_data['author_url'] if 'author_url' in dict_data \
            else 'undefined_author_url'
        self.aurl = dict_data['aurl'] if 'aurl' in dict_data \
            else kwargs['aurl'] if 'aurl' in kwargs \
            else 'undefined_aurl'
        self.message = dict_data['message'] if 'message' in dict_data \
            else kwargs['message'] if 'message' in kwargs \
            else 'undefined_message'
        self.turl = dict_data['turl'] if 'turl' in dict_data \
            else kwargs['turl'] if 'turl' in kwargs \
            else 'undefined_turl'
        self.type = dict_data['type'] if 'type' in dict_data \
            else kwargs['type'] if 'type' in kwargs \
            else 'long'
        self.media_files = dict_data['media_files'] if 'media_files' in dict_data \
            else kwargs['media_files'] if 'media_files' in kwargs \
            else []
        self.document_file = dict_data['document_file'] if 'document_file' in dict_data \
            else kwargs['document_file'] if 'document_file' in kwargs \
            else None

    def to_dict(self):
        return {
            'category': self.category,
            'title': self.title,
            'text': self.text,
            'author': self.author,
            'author_url': self.author_url,
            'aurl': self.aurl,
            'message': self.message,
            'turl': self.turl,
            'type': self.type,
            'media_files': self.media_files
        }


def new_weibo_converter(url, **kwargs):
    try:
        wurl = url
        if wurl.find('weibo.com'):
            wurl = wurl.replace('weibo.com', 'm.weibo.cn')
        wb = weibo.Weibo(wurl).new_get_weibo()
        print('get weibo item')
        if not wb:
            raise NoItemFoundException('No weibo found')
        if wb['type'] == 'long':
            temp_html = DocumentPreprocessor(wb['content'])
            temp_html.upload_all_images()
            temp_content = temp_html.get_processed_html()
            tdict = TelegraphDict(wb, content=temp_content).to_dict()
            print('get telegraph dict: ' + str(tdict))
            t_url = get_telegraph_url(tdict)
        else:
            t_url = ''
        mdict = MetadataDict(wb, category='weibo', turl=t_url, message='').to_dict()
        print(mdict)
        return mdict
    except Exception as e:
        print('weibo_scraping_failed')
        print(traceback.format_exc())
        raise


def twitter_converter(url, **kwargs):
    try:
        turl = url
        tw = twitter.Twitter(turl, **kwargs).get_tweet_item()
        print('get twitter item')
        if not tw:
            raise NoItemFoundException('No twitter found')
        if tw['type'] == 'long':
            t_url = get_telegraph_url(tw)
        else:
            t_url = ''
        mdict = MetadataDict(tw, category='twitter', turl=t_url, message='').to_dict()
        print(mdict)
        return mdict
    except Exception as e:
        print('twitter_scraping_failed')
        print(traceback.format_exc())
        raise


def douban_converter(url, **kwargs):
    try:
        durl = url
        db = douban.Douban(url=durl).get_fav_item()
        print('get douban item')
        if not db:
            raise NoItemFoundException('No douban found')
        if db['type'] == 'long':
            t_url = get_telegraph_url(db)
        else:
            t_url = ''
        mdict = MetadataDict(db, category='Douban', turl=t_url, message='').to_dict()
        print(mdict)
        return mdict
    except Exception as e:
        print('douban_scraping_failed')
        print(traceback.format_exc())
        raise


def zhihu_converter(url, **kwargs):
    try:
        zurl = url
        zh = zhihu.Zhihu(url=zurl).get_fav_item()
        print('get zhihu item')
        if not zh:
            raise NoItemFoundException('No zhihu found')
        if zh['type'] == 'long':
            t_url = get_telegraph_url(zh)
        else:
            t_url = ''
        mdict = MetadataDict(zh, category='zhihu', turl=t_url, message='').to_dict()
        print(mdict)
        return mdict
    except Exception as e:
        print('zhihu_scraping_failed')
        print(traceback.format_exc())
        raise


def instagram_converter(url, **kwargs):
    try:
        iurl = url
        ins = instagram.Instagram(url=iurl).get_single_ins_item()
        print('get instagram item')
        if not ins:
            raise NoItemFoundException('No instagram found')
        if ins['type'] == 'long':
            t_url = get_telegraph_url(ins)
        else:
            t_url = ''
        mdict = MetadataDict(ins, category='Instagram', turl=t_url, message='').to_dict()
        print(mdict)
        return mdict
    except Exception as e:
        print('instagram_scraping_failed')
        print(traceback.format_exc())


def threads_converter(url, **kwargs):
    try:
        threads_url = url
        th = threads.Threads(url=threads_url).get_threads()
        print('get threads item')
        if not th:
            raise NoItemFoundException('No threads found')
        if th['type'] == 'long':
            t_url = get_telegraph_url(th)
        else:
            t_url = ''
        mdict = MetadataDict(th, category='Threads', turl=t_url, message='').to_dict()
        print(mdict)
        return mdict
    except Exception as e:
        print('threads_scraping_failed')
        print(traceback.format_exc())


def inoreader_converter(request_data, **kwargs):
    try:
        ino = request_data
        if util.get_html_text_length(ino['content']) > 200:
            ino['type'] = 'long'
        else:
            ino['type'] = 'short'
        print('get inoreader url: '+ino['aurl'])
        print('get inoreader item')
        if not ino:
            raise NoItemFoundException('No inoreader found')
        soup = BeautifulSoup(ino['content'], 'html.parser')
        ino['media_files'] = []
        for img in soup.find_all('img'):
            media_item = {'type': 'image', 'url': img['src'], 'caption':''}
            ino['media_files'].append(media_item)
            img.extract()
        for p in soup.find_all('p'):
            p.unwrap()
        for span in soup.find_all('span'):
            span.unwrap()
        ino['text'] = str(soup).replace('<br/>', '\n')
        ino['text'] = '<a href="' + ino['aurl'] + '">' + ino['author'] + '</a>: ' + ino['text']
        t_url = get_telegraph_url(ino)
        ino['message'] = ino['message'] + '\n' if ino['message'] else ''
        mdict = MetadataDict(ino, category=ino['tag'], turl=t_url, message=ino['message']).to_dict()
        print(mdict)
        return mdict
    except Exception as e:
        print('inoreader_scraping_failed')
        print(traceback.format_exc())
        raise


def get_telegraph_url(tdict, failure_limitation=5, upload_images=True):
    failure_counter = 0
    telegraph_url = ''
    if upload_images:
        temp_html = DocumentPreprocessor(tdict['content'])
        temp_html.upload_all_images()
        temp_content = temp_html.get_processed_html()
        tdict = TelegraphDict(tdict, content=temp_content).to_dict()
    else:
        tdict = TelegraphDict(tdict).to_dict()
    while failure_counter < failure_limitation:
        try:
            telegraph_url = telegraph_convert(tdict)
            if telegraph_url != 'nothing':
                break
        except Exception as e:
            failure_counter += 1
            print('failed'+str(failure_counter)+'times')
            print(traceback.format_exc())
            continue
    print('get telegraph dict: ' + str(tdict))
    return telegraph_url


def telegraph_convert(tdict):
    res = ''
    # try:
    metadata_dict = tdict
    author = 'author'
    author_url = 'author_url'
    print('content of argument:' + str(metadata_dict))
    t = TelegraphPoster(use_api=True)
    short_name = metadata_dict[author]
    t.create_api_token(short_name[0:14], author_name=metadata_dict[author])
    telegraphPost = t.post(title=metadata_dict['title'], author=metadata_dict[author],
                           text=metadata_dict['content'], author_url=metadata_dict[author_url])
    print('telegraph url:' + telegraphPost['url'])
    res = telegraphPost['url']
    # except Exception as e:
    #     print(traceback.format_exc())
    # finally:
    return res if res else 'nothing'


def video_converter(url, **kwargs):
    try:
        v = videos.VideoConverter(url=url, **kwargs).get_video_item()
        print('get video item')
        if not v:
            raise Exception('No video found')
        mdict = MetadataDict(v, category='video', message='', type='short').to_dict()
        print(mdict)
        return mdict
    except Exception as e:
        print('video_scraping_failed')
        print(traceback.format_exc())
