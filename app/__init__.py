# -*- coding:utf-8 -*-
from flask import Flask
import json
from flask import request
from html_telegraph_poster import TelegraphPoster
from html_telegraph_poster.utils import DocumentPreprocessor
import threading
import traceback

import app.api_functions
from . import atelebot, combination, settings
from .api_functions import *
from .utils import telegraph, util
from .converter import zhihu, twitter, douban, weibo
import time
import asyncio


# from time import sleep
# import toml


# from .verify import check


def create_app():
    server = Flask(__name__)
    c_title = ""
    c_list = [""]
    site_url = 'http://' + settings.env_var.get('SITE_URL', '127.0.0.1:' + settings.env_var.get('PORT', '1045'))
    default_channel = settings.env_var.get('CHANNEL_ID', '')
    print(site_url)
    print(settings.env_var.get('PORT', 'no port'))
    telegraph_url = site_url + '/telegraphConvert'

    @server.route('/newWeiboConvert', methods=['get', 'post'])
    def newWeiboConvert():
        try:
            weibo_data = request.get_data()
            response_data = new_weibo_converter(weibo_data)
            return response_data
        except Exception:
            print(traceback.format_exc())
            return False

    @server.route('/weiboConvert', methods=['get', 'post'])
    def weibo_convert():
        try:
            weiboData = request.get_data()
            wdict = json.loads(weiboData)
        except Exception:
            print(traceback.format_exc())
            return False
        return 'ok'

    @server.route('/doubanConvert', methods=['get', 'post'])
    def douban_convert():
        try:
            douban_data = request.get_data()
            response_data = douban_converter(douban_data)
            return response_data
        except Exception:
            print(traceback.format_exc())
            return False

    @server.route('/twitterConvert', methods=['get', 'post'])
    def twitter_convert():
        try:
            twitter_data = request.get_data()
            response_data = douban_converter(twitter_data)
            return response_data
        except Exception:
            print(traceback.format_exc())
            return False

    @server.route('/zhihuConvert', methods=['get', 'post'])
    def zhihu_convert():
        try:
            zhihu_data = request.get_data()
            response_data = zhihu_converter(zhihu_data)
            return response_data
        except Exception:
            print(traceback.format_exc())
            return False

    @server.route('/inoreaderConvert', methods=['get', 'post'])
    def inoreader_convert():
        try:
            inoreader_data = request.get_data()
            data_dict = json.loads(inoreader_data)
            mdict = inoreader_converter(data_dict)
            atelebot.send_formatted_message(data=mdict,channel_id=default_channel)
        except Exception:
            print(traceback.format_exc())
            return 'Failed'
        return mdict

    @server.route('/telegraphConvert', methods=['get', 'post'])
    def telegraph_convert(check=True):
        return 'ok'

    # if settings.env_var.get('BOT', 'True') == 'True':
    telebot_thread = threading.Thread(target=atelebot.bot.polling, daemon=True)
    telebot_thread.start()  # start the bot in a thread instead

    return server
