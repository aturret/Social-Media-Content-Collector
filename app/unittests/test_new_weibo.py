import pytest
from app.converter import weibo
# from app.atelebot import send_to_channel
import telebot

bot = telebot.TeleBot('5684876402:AAH_GVpGi2G_FRI6JVkR7ba-2UIrSdZDxgg')
channel_id = '@aturretnotification'


def test_weibo_video_tag():
    w = weibo.Weibo(url='https://weibo.com/1770694027/MzDQCh6LO')
    return w.new_get_weibo()


def test_weibo_emoji_tag():
    w = weibo.Weibo(url='https://m.weibo.cn/status/MCAqGFsQL')
    return w.new_get_weibo()


def test_weibo_forward_image_link():
    w = weibo.Weibo(url='https://m.weibo.cn/status/MCAOYhYM3')
    return w.new_get_weibo()


def test_weibo_multiple_pics():
    w = weibo.Weibo(url='https://weibo.com/5158759582/MBXXcFJQD')
    return w.new_get_weibo()


def test_weibo_multiple_videos():
    w = weibo.Weibo(url='https://m.weibo.cn/status/MBY95pZ2g')
    return w.new_get_weibo()


def test_weibo_live_photos():
    w = weibo.Weibo(url='https://weibo.com/5709895523/MC0iGmhaR')
    return w.new_get_weibo()


def test_weibo_rt():
    w = weibo.Weibo(url='https://weibo.com/2656274875/MARShsRK7')
    return w.new_get_weibo()


def test_no_weibo_found():
    w = weibo.Weibo(url='https://weibo.com/status/7714699796')
    return w.new_get_weibo()


pytest