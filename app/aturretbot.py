import telebot
import re
import requests
import json

bot = telebot.TeleBot("931723693:AAFN453UJxlrPX8ilzKL2bFp2---QNLRQrA")
weiboApiUrl = 'http://api.aturret.top/weiboConvert'
twitterApiUrl = 'http://api.aturret.top/twitterConvert'
zhihuApiUrl = 'http://api.aturret.top/zhihuConvert'
doubanApiUrl = 'http://api.aturret.top/doubanConvert'

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
    if url.find('weibo.com') or url.find('m.weibo.cn'):
        requests.post(url=weiboApiUrl,data=json.dumps(data))
        print('检测到微博URL，转化中')
    elif url.find('twitter.com'):
        requests.post(url=twitterApiUrl,data=json.dumps(data))
        print('检测到TwitterURL，转化中')
    elif url.find('zhihu.com'):
        requests.post(url=zhihuApiUrl,data=json.dumps(data))
        print('检测到知乎URL，转化中')
    elif url.find('douban.com'):
        requests.post(url=doubanApiUrl,data=json.dumps(data))
        print('检测到豆瓣URL，转化中')
    else:
        print('不符合规范，无法转化')




# bot.infinity_polling()