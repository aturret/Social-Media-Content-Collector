import traceback
import telebot
from telebot.async_telebot import AsyncTeleBot
import re
import requests
import json
from . import settings
from .utils import util
# import toml
# import yaml
site_url = settings.env_var.get('SITE_URL', '127.0.0.1:' + settings.env_var.get('PORT', '1045'))
telebot_key = settings.env_var.get('TELEGRAM_BOT_KEY')
channel_id = settings.env_var.get('CHANNEL_ID', None)
youtube_api = settings.env_var.get('YOUTUBE_API', None)

bot = AsyncTeleBot(telebot_key)
weiboApiUrl = 'http://' + site_url + '/weiboConvert'
twitterApiUrl = 'http://' + site_url + '/twitterConvert'
zhihuApiUrl = 'http://' + site_url + '/zhihuConvert'
doubanApiUrl = 'http://' + site_url + '/doubanConvert'
mustodonApiUrl = 'http://' + site_url + '/mustodonConvert'

urlpattern = re.compile(r'(http|https)://([\w.!@#$%^&*()_+-=])*\s*')  # 只摘取httpURL的pattern
# no_telegraph_regexp="weibo\.com|m\.weibo\.cn|twitter\.com|zhihu\.com|douban\.com"
no_telegraph_regexp="youtube\.com|bilibili\.com"
# no_telegraph_list = ['',]
@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    await bot.reply_to(message, "fku")


@bot.message_handler(regexp="(http|https)://([\w.!@#$%^&*()_+-=])*\s*")
async def get_social_media(message):
    url = urlpattern.search(message.text).group()
    print('the url is: '+url)
    target_url = ''
    data = {'url': url}
    t = None
    if url.find('weibo.com') != -1 or url.find('m.weibo.cn') != -1:
        await bot.reply_to(message, '检测到微博URL，转化中\nWeibo URL detected, converting...')
        print('检测到微博URL，转化中\nWeibo URL detected, converting...')
        target_url = weiboApiUrl
    elif url.find('twitter.com') != -1:
        await bot.reply_to(message, '检测到TwitterURL，转化中\nTwitter URL detected, converting...')
        print('检测到TwitterURL，转化中\nTwitter URL detected, converting...')
        target_url = twitterApiUrl
    elif url.find('zhihu.com') != -1:
        await bot.reply_to(message, '检测到知乎URL，转化中\nZhihu URL detected, converting...')
        print('检测到知乎URL，转化中\nZhihu URL detected, converting...')
        target_url = zhihuApiUrl
    elif url.find('douban.com') != -1:
        await bot.reply_to(message, '检测到豆瓣URL，转化中\nDouban URL detected, converting...')
        print('检测到豆瓣URL，转化中\nDouban URL detected, converting...')
        target_url = doubanApiUrl
    elif url.find('youtube.com') != -1:
        if not youtube_api:
            await bot.reply_to(message, '未配置YouTube API，无法抓取\nYouTube API is not configured. Cannot extract metadata from YouTube.')
        else:
            await bot.reply_to(message, '检测到YouTubeURL，转化中\nYouTube URL detected, converting...')
    else:
        if '_mastodon_session' in requests.utils.dict_from_cookiejar(util.get_response(url).cookies):
            await bot.reply_to(message, '检测到长毛象URL，转化中\nMustodon URL detected, converting...')
            print('检测到长毛象URL，转化中\nMustodon URL detected, converting...')
            target_url = mustodonApiUrl
        else:
            await bot.reply_to(message, '不符合规范，无法转化\ninvalid URL detected, cannot convert')
            print('不符合规范，无法转化\ninvalid URL detected, cannot convert')
            return False
    response = requests.post(url=target_url, data=json.dumps(data))
    print(response.status_code)
    if response.status_code == 200:
        t = response.json()
        print(type(t))
        print(t)
    else:
        print('Failure')
        await bot.reply_to(message, 'Failure')
    if t and channel_id:
        send_to_channel(data=t, message=message)


def send_to_channel(data, message=None):
    try:
        if re.search(no_telegraph_regexp,data['aurl']):
            text = '<a href=\"' + data['aurl'] + '\">' \
               '<b>' + data['title'] + '</b></a>\n' \
               'via #' + data['category'] + \
               ' - <a href=\"' + data['originurl'] + ' \"> ' \
               + data['origin'] + '</a>\n' + data['message']
        else:
            text = '<a href=\"' + data['turl'] + '\">' \
               '<b>' + data['title'] + '</b></a>\n' \
               'via #' + data['category'] + \
               ' - <a href=\"' + data['originurl'] + ' \"> ' \
               + data['origin'] + '</a>\n' + data['message'] + \
               '<a href=\"' + data['aurl'] + '\">阅读原文</a>'
        print(text)
        bot.send_message(chat_id=channel_id, parse_mode='html', text=text)
    except Exception:
        if message:
            bot.reply_to(message, 'Failure')
        print(traceback.format_exc())

# bot.infinity_polling()
