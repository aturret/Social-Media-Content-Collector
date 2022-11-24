import telebot
import re
import requests
import json
import toml
# import yaml

with open("./app/config.toml", 'r') as tfile:
#     cfg = yaml.load(ymlfile)
    cfg = toml.load(tfile)

bot = telebot.TeleBot(cfg['telegram']['bot_key'])
weiboApiUrl = 'http://'+cfg['site']['url']+'/weiboConvert'
twitterApiUrl = 'http://'+cfg['site']['url']+'/twitterConvert'
zhihuApiUrl = 'http://'+cfg['site']['url']+'/zhihuConvert'
doubanApiUrl = 'http://'+cfg['site']['url']+'/doubanConvert'

urlpattern = re.compile(r'(http|https)://([\w.!@#$%^&*()_+-=])*\s*') #只摘取httpURL的pattern

# @bot.message_handler(regexp="weibo\.com|m\.weibo\.cn")
# def weibo(message):
#     weiboUrl = urlpattern.search(message.text).group()
#     weiboData = {'url':weiboUrl}
#     requests.post(url=weiboApiUrl,data=json.dumps(weiboData))
#
# @bot.message_handler(regexp="twitter\.com")
# def twitter(message):
#     twitterUrl = urlpattern.search(message.text).group()
#     twitterData = {'url':twitterUrl}
#     requests.post(url=twitterApiUrl,data=json.dumps(twitterData))
#
# @bot.message_handler(regexp="zhihu\.com")
# def zhihu(message):
#     zhihuUrl = urlpattern.search(message.text).group()
#     zhihuData = {'url':zhihuUrl}
#     requests.post(url=zhihuApiUrl,data=json.dumps(zhihuData))

# @bot.message_handler(regexp="douban\.com")
# def douban(message):
#     zhihuUrl = urlpattern.search(message.text).group()
#     zhihuData = {'url':zhihuUrl}
#     requests.post(url=zhihuApiUrl,data=json.dumps(zhihuData))

@bot.message_handler(regexp="weibo\.com|m\.weibo\.cn|twitter\.com|zhihu\.com|douban\.com")
def get_social_media(message):
    url = urlpattern.search(message.text).group()
    data = {'url':url}
    if url.find('weibo.com') != -1 or url.find('m.weibo.cn') != -1:
        requests.post(url=weiboApiUrl,data=json.dumps(data))
        print('检测到微博URL，转化中\nWeibo URL detected, converting...')
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




# bot.infinity_polling()