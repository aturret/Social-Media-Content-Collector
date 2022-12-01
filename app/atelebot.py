import traceback
import telebot
import re
import requests
import json
from . import settings
# import toml
# import yaml
site_url = settings.env_var.get('SITE_URL', '127.0.0.1:' + settings.env_var.get('PORT', '1045'))
telebot_key = settings.env_var.get('TELEGRAM_BOT_KEY')
channel_id = settings.env_var.get('CHANNEL_ID', None)

bot = telebot.TeleBot(telebot_key)
weiboApiUrl = 'http://' + site_url + '/weiboConvert'
twitterApiUrl = 'http://' + site_url + '/twitterConvert'
zhihuApiUrl = 'http://' + site_url + '/zhihuConvert'
doubanApiUrl = 'http://' + site_url + '/doubanConvert'

urlpattern = re.compile(r'(http|https)://([\w.!@#$%^&*()_+-=])*\s*')  # 只摘取httpURL的pattern


@bot.message_handler(regexp="weibo\.com|m\.weibo\.cn|twitter\.com|zhihu\.com|douban\.com")
def get_social_media(message):
    url = urlpattern.search(message.text).group()
    print('the url is: '+url)
    target_url = ''
    data = {'url': url}
    t = None
    if url.find('weibo.com') != -1 or url.find('m.weibo.cn') != -1:
        bot.reply_to(message, '检测到微博URL，转化中\nWeibo URL detected, converting...')
        print('检测到微博URL，转化中\nWeibo URL detected, converting...')
        target_url = weiboApiUrl
    elif url.find('twitter.com') != -1:
        bot.reply_to(message, '检测到TwitterURL，转化中\nTwitter URL detected, converting...')
        print('检测到TwitterURL，转化中\nTwitter URL detected, converting...')
        target_url = twitterApiUrl
    elif url.find('zhihu.com') != -1:
        bot.reply_to(message, '检测到知乎URL，转化中\nZhihu URL detected, converting...')
        print('检测到知乎URL，转化中\nZhihu URL detected, converting...')
        target_url = zhihuApiUrl
    elif url.find('douban.com') != -1:
        bot.reply_to(message, '检测到豆瓣URL，转化中\nDouban URL detected, converting...')
        print('检测到豆瓣URL，转化中\nDouban URL detected, converting...')
        target_url = doubanApiUrl
    else:
        print('不符合规范，无法转化\ninvalid URL detected, cannot convert')
    response = requests.post(url=target_url, data=json.dumps(data))
    print(response.status_code)
    if response.status_code == 200:
        t = response.json()
        print(type(t))
        print(t)
    else:
        print('Failure')
        bot.reply_to(message, 'Failure')
    if t and channel_id:
        send_to_channel(data=t, message=message)


def send_to_channel(data, message=None):
    try:
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
