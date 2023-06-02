# -*- coding:utf-8 -*-
import asyncio
import traceback
from quart import Quart, request
import sentry_sdk
from sentry_sdk.integrations.quart import QuartIntegration
import threading
from . import api_functions
from . import atelebot, combination, settings, bot_start
# from .api_functions import *
from .utils import telegraph
from .utils import util
from telebot import types

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
            QuartIntegration(),
        ],
        traces_sample_rate=1.0
    )




async def create_app():
    server = Quart(__name__)
    default_channel = settings.env_var.get('CHANNEL_ID', '')

    print(settings.env_var.get('PORT', 'no port'))

    @server.route('/newWeiboConvert', methods=['get', 'post'])
    async def newWeiboConvert():
        try:
            weibo_data = await request.get_data()
            response_data = await api_functions.new_weibo_converter(weibo_data)
            return response_data
        except Exception:
            print(traceback.format_exc())
            return False

    @server.route('/weiboConvert', methods=['get', 'post'])
    async def weibo_convert():
        try:
            weiboData = await request.get_data()
            wdict = util.json.loads(weiboData)
        except Exception:
            print(traceback.format_exc())
            return False
        return 'ok'

    @server.route('/doubanConvert', methods=['get', 'post'])
    async def douban_convert():
        try:
            douban_data = await request.get_data()
            response_data = await api_functions.douban_converter(douban_data)
            return response_data
        except Exception:
            print(traceback.format_exc())
            return False

    @server.route('/twitterConvert', methods=['get', 'post'])
    async def twitter_convert():
        try:
            twitter_data = await request.get_data()
            if twitter_data == b'':
                return 'ok'
            response_data = await api_functions.twitter_converter(twitter_data)
            return response_data
        except Exception:
            print(traceback.format_exc())
            return False

    @server.route('/zhihuConvert', methods=['get', 'post'])
    async def zhihu_convert():
        try:
            zhihu_data = request.get_data()
            response_data = await api_functions.zhihu_converter(zhihu_data)
            return response_data
        except Exception:
            print(traceback.format_exc())
            return False

    @server.route('/inoreaderConvert', methods=['post'])
    async def inoreader_convert():
        try:
            inoreader_data = await request.get_data()
            data_dict = util.json.loads(inoreader_data)
            mdict = api_functions.inoreader_converter(data_dict)
            await atelebot.send_formatted_message(data=mdict, chat_id=default_channel)
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

    @server.route('/', methods=['get', 'post', 'head'])
    def ping():
        print('hello, world!')
        return 'pong', 200

    @server.route('/bot', methods=['post'])
    async def webhook():
        request_type = request.headers.get('content-type')
        if request_type == 'application/json':
            json_string = await request.get_data()
            json_string = json_string.decode('utf-8')
            update = types.Update.de_json(json_string)
            print(update)
            updates = [update]
        else:
            return '', 403
        await atelebot.bot.process_new_updates(updates)
        return '', 200

    @server.route('/debug-sentry')
    def trigger_error():
        division_by_zero = 1 / 0

    return server


if settings.env_var.get('BOT', 'True') == 'True':
    # telebot_thread = threading.Thread(target=bot_start.bot_polling(), daemon=True)
    telebot_thread = threading.Thread(target=atelebot.bot.polling(non_stop=True, timeout=telebot_timeout),
                                      daemon=True)
    telebot_thread.start()
