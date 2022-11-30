import telebot
import re
import requests
import json
import toml
from . import settings
# import yaml
site_url = settings.env_var.get('SITE_URL','127.0.0.1:'+settings.env_var.get('PORT','1045'))
telebot_key = settings.env_var.get('TELEGRAM_BOT_KEY')
channel_id = settings.env_var.get('CHANNEL_ID',None)

bot = telebot.TeleBot(telebot_key)
weiboApiUrl = 'http://'+site_url+'/weiboConvert'
twitterApiUrl = 'http://'+site_url+'/twitterConvert'
zhihuApiUrl = 'http://'+site_url+'/zhihuConvert'
doubanApiUrl = 'http://'+site_url+'/doubanConvert'

urlpattern = re.compile(r'(http|https)://([\w.!@#$%^&*()_+-=])*\s*') #只摘取httpURL的pattern





@bot.message_handler(regexp="weibo\.com|m\.weibo\.cn|twitter\.com|zhihu\.com|douban\.com")
def get_social_media(message):
    url = urlpattern.search(message.text).group()
    data = {'url':url}
    t = None
    if url.find('weibo.com') != -1 or url.find('m.weibo.cn') != -1:
        bot.reply_to(message,'检测到微博URL，转化中\nWeibo URL detected, converting...')
        print('检测到微博URL，转化中\nWeibo URL detected, converting...')
        t = requests.post(url=weiboApiUrl, data=json.dumps(data)).json()
        print(type(t))
        print(t)
    elif url.find('twitter.com') != -1:
        requests.post(url=twitterApiUrl,data=json.dumps(data))
        print('检测到TwitterURL，转化中\nTwitter URL detected, converting...')
    elif url.find('zhihu.com') != -1:
        requests.post(url=zhihuApiUrl,data=json.dumps(data))
        print('检测到知乎URL，转化中\nZhihu URL detected, converting...')
    elif url.find('douban.com') != -1:
        requests.post(url=doubanApiUrl,data=json.dumps(data))
        print('检测到豆瓣URL，转化中\nDouban URL detected, converting...')
    else:
        print('不符合规范，无法转化\ninvalid URL detected, cannont convert')
    if t and channel_id:
        text = '<a href=\"'+ t['turl'] +'\">' \
               '<b>'+ t['title'] +'</b></a>\n' \
               'via #'+ t['category'] +\
               ' - <a href=\"'+ t['originurl'] +' \"> ' \
               + t['origin']+'</a>\n' + t['message'] + \
               '<a href=\"'+ t['aurl'] +'\">阅读原文</a>'
        print(text)
        bot.send_message(chat_id=channel_id,parse_mode='html',text=text)




# bot.infinity_polling()