import telebot
import re
import requests
import json

bot = telebot.TeleBot("931723693:AAFN453UJxlrPX8ilzKL2bFp2---QNLRQrA")
weiboApiUrl = 'http://api.aturret.top/weiboConvert'
twitterApiUrl = 'http://api.aturret.top/twitterConvert'

urlpattern = re.compile(r'(http|https)://([\w.!@#$%^&*()_+-=])*\s*') #只摘取httpURL的pattern

@bot.message_handler(regexp="weibo\.com|m\.weibo\.cn")
def weibo(message):
    weiboUrl = urlpattern.search(message.text).group()
    weiboData = {'url':weiboUrl}
    requests.post(url=weiboApiUrl,data=json.dumps(weiboData))

@bot.message_handler(regexp="twitter\.com")
def twitter(message):
    twitterUrl = urlpattern.search(message.text).group()
    twitterData = {'url':twitterUrl}
    requests.post(url=twitterApiUrl,data=json.dumps(twitterData))

# bot.infinity_polling()