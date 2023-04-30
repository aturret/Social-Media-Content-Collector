# -*- coding:utf-8 -*-
from flask import Flask
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import request
import threading
import app.api_functions
from . import atelebot, combination, settings, bot_start
from .api_functions import *
from .utils import telegraph
from .utils.util import *

sentry_on = settings.env_var.get('SENTRY_ON', 'False')
sentry_dsn = settings.env_var.get('SENTRY_DSN', '')
telebot_timeout = int(settings.env_var.get('TELEBOT_TIMEOUT', '60'))
# from time import sleep
# import toml


# from .verify import check
if sentry_on == 'True':
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[
            FlaskIntegration(),
        ],
        traces_sample_rate=1.0
    )


def create_app():
    server = Flask(__name__)
    default_channel = settings.env_var.get('CHANNEL_ID', '')

    print(settings.env_var.get('PORT', 'no port'))

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
            if twitter_data == b'':
                return 'ok'
            response_data = twitter_converter(twitter_data)
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
            atelebot.send_formatted_message(data=mdict, channel_id=default_channel)
        except Exception:
            print(traceback.format_exc())
            return 'Failed'
        return mdict

    @server.route('/telegraphConvert', methods=['get', 'post'])
    def telegraph_convert():
        return 'ok', 200

    @server.route('/rachelConvert', methods=['get', 'post'])
    def rachel_convert():
        return 'ok', 200

    @server.route('/ping', methods=['get', 'post', 'head'])
    def ping():
        print('hello, world!')
        return 'pong', 200

    @server.route('/debug-sentry')
    def trigger_error():
        division_by_zero = 1 / 0

    # start the bot in a thread instead

    return server




if settings.env_var.get('BOT', 'True') == 'True':
    # telebot_thread = threading.Thread(target=bot_start.bot_polling(), daemon=True)
    telebot_thread = threading.Thread(target=atelebot.bot.polling(non_stop=True, timeout=telebot_timeout),
                                      daemon=True)
    telebot_thread.start()
