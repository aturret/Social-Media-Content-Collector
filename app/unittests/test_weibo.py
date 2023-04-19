import pytest
from app.converter import weibo




def test_weibo_video_tag():
    w = weibo.Weibo(url='https://m.weibo.cn/status/4884946584077604')

    return w.get_weibo()

def test_weibo_emoji_tag():
    w = weibo.Weibo(url='https://m.weibo.cn/status/MCAqGFsQL')
    return w.get_weibo()

def test_weibo_forward_image_link():
    w = weibo.Weibo(url='https://m.weibo.cn/status/MCAOYhYM3')
    return w.get_weibo()

def test_weibo_multiple_videos():
    w = weibo.Weibo(url='https://m.weibo.cn/status/MBY95pZ2g')
    return w.get_weibo()




pytest