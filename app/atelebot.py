import traceback
import telebot
import re
import requests
import json
from . import settings
from .utils import util

site_url = settings.env_var.get('SITE_URL', '127.0.0.1:' + settings.env_var.get('PORT', '1045'))
telebot_key = settings.env_var.get('TELEGRAM_BOT_KEY')
default_channel_id = settings.env_var.get('CHANNEL_ID', None)
youtube_api = settings.env_var.get('YOUTUBE_API', None)

bot = telebot.TeleBot(telebot_key)
# weiboApiUrl = 'http://' + site_url + '/weiboConvert'
weiboApiUrl = 'http://' + site_url + '/newWeiboConvert'
twitterApiUrl = 'http://' + site_url + '/twitterConvert'
zhihuApiUrl = 'http://' + site_url + '/zhihuConvert'
doubanApiUrl = 'http://' + site_url + '/doubanConvert'
mustodonApiUrl = 'http://' + site_url + '/mustodonConvert'

urlpattern = re.compile(r'(http|https)://([\w.!@#$%^&*()_+-=])*\s*')  # 只摘取httpURL的pattern
# no_telegraph_regexp="weibo\.com|m\.weibo\.cn|twitter\.com|zhihu\.com|douban\.com"
no_telegraph_regexp = "youtube\.com|bilibili\.com"
# no_telegraph_list = ['',]
formatted_data = []


@bot.message_handler(regexp="(http|https)://([\w.!@#$%^&*()_+-=])*\s*")
def get_social_media(message):
    try:
        markup = telebot.types.InlineKeyboardMarkup()
        buttons = []

        url = urlpattern.search(message.text).group()
        print('the url is: ' + url)
        target_url = ''
        data = {'url': url}
        response_data = None
        if url.find('weibo.com') != -1 or url.find('m.weibo.cn') != -1:
            replying_message = bot.reply_to(message, '检测到微博URL，转化中\nWeibo URL detected, converting...')
            print('检测到微博URL，转化中\nWeibo URL detected, converting...')
            target_url = weiboApiUrl
        elif url.find('twitter.com') != -1:
            replying_message = bot.reply_to(message, '检测到TwitterURL，转化中\nTwitter URL detected, converting...')
            print('检测到TwitterURL，转化中\nTwitter URL detected, converting...')
            target_url = twitterApiUrl
        elif url.find('zhihu.com') != -1:
            replying_message = bot.reply_to(message, '检测到知乎URL，转化中\nZhihu URL detected, converting...')
            print('检测到知乎URL，转化中\nZhihu URL detected, converting...')
            target_url = zhihuApiUrl
        elif url.find('douban.com') != -1:
            replying_message = bot.reply_to(message, '检测到豆瓣URL，转化中\nDouban URL detected, converting...')
            print('检测到豆瓣URL，转化中\nDouban URL detected, converting...')
            target_url = doubanApiUrl
        elif url.find('youtube.com') != -1:
            if not youtube_api:
                bot.reply_to(message,
                             '未配置YouTube API，无法抓取\nYouTube API is not configured. Cannot extract metadata from YouTube.')
            else:
                replying_message = bot.reply_to(message, '检测到YouTubeURL，转化中\nYouTube URL detected, converting...')
        else:
            if '_mastodon_session' in requests.utils.dict_from_cookiejar(util.get_response(url).cookies):
                replying_message = bot.reply_to(message, '检测到长毛象URL，转化中\nMustodon URL detected, converting...')
                print('检测到长毛象URL，转化中\nMustodon URL detected, converting...')
                target_url = mustodonApiUrl
            else:
                bot.reply_to(message, '不符合规范，无法转化\ninvalid URL detected, cannot convert')
                print('不符合规范，无法转化\ninvalid URL detected, cannot convert')
                return False
        response = requests.post(url=target_url, data=json.dumps(data))
        if response.status_code == 200:
            response_data = response.json()
            formatted_data.pop() if len(formatted_data) > 0 else None
            formatted_data.append(response_data)
        else:
            print('Failure')
            bot.reply_to(message, 'Failure')
            return
        bot.delete_message(message.chat.id, replying_message.message_id) if replying_message else None
        if default_channel_id:
            forward_button = telebot.types.InlineKeyboardButton(text='发送到频道',
                                                                callback_data='chan+{}'.format(default_channel_id))
            buttons.append(forward_button)
        show_button = telebot.types.InlineKeyboardButton(text='发送到私聊',
                                                         callback_data='priv+{}'.format(message.chat.id))
        buttons.append(show_button)
        extract_button = telebot.types.InlineKeyboardButton(text='强制提取',
                                                         callback_data='extr+{}'.format(message.chat.id))
        buttons.append(extract_button)
        if len(buttons) > 0:
            markup.add(*buttons)
            bot.send_message(message.chat.id, "选择您想要的操作：", reply_markup=markup)
        else:
            if buttons[0].callback_data == 'private':
                send_formatted_message(data=response_data)
            elif buttons[0].callback_data == 'channel':
                send_to_channel(data=response_data)
    except Exception as e:
        print(traceback.format_exc())
        bot.reply_to(message, 'Failure'+traceback.format_exc())
        return


@bot.callback_query_handler(func=lambda call: call.data.startswith('chan'))
def callback_query(call):
    try:
        if len(formatted_data) == 0:
            bot.reply_to(call.message, "No data to send")
            bot.answer_callback_query(call.id, "No data to send")
            raise Exception('No data to send')
        the_data = formatted_data.pop()
        send_to_channel(data=the_data, channel_id=call.data.split('+')[1])
        bot.answer_callback_query(call.id, "Message sent to channel")
    except Exception as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure")
    finally:
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)



@bot.callback_query_handler(func=lambda call: call.data.startswith('priv'))
def callback_query(call):
    try:
        if len(formatted_data) == 0:
            bot.reply_to(call.message, "No data to send")
            bot.answer_callback_query(call.id, "No data to send")
            raise Exception('No data to send')
        the_data = formatted_data.pop()
        send_formatted_message(data=the_data, message=call.message, chat_id=call.message.chat.id)
        bot.answer_callback_query(call.id, "Message sent to channel")
    except Exception as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure")
    finally:
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)



@bot.callback_query_handler(func=lambda call: call.data.startswith('extr'))
def callback_query(call):
    try:
        if len(formatted_data) == 0:
            bot.reply_to(call.message, "No data to send")
            bot.answer_callback_query(call.id, "No data to send")
            raise Exception('No data to send')
        the_data = formatted_data.pop()
        the_data['type'] = 'short'
        send_formatted_message(data=the_data, message=call.message, chat_id=call.message.chat.id)
        bot.answer_callback_query(call.id, "Message sent to channel")
    except Exception as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure")
    finally:
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


def send_formatted_message(data, message=None,chat_id=None,telegram_bot=bot):
    if not chat_id:
        chat_id = message.chat.id
    try:
        if data['type'] == 'short' and data['media_files'] and len(data['media_files']) > 0:
            caption_text = data['text'] + '\n#' + data['category']
            media_group = media_files_packaging(data['media_files'], caption_text)
            telegram_bot.send_media_group(chat_id=chat_id, media=media_group)
        else:
            text = message_formatting(data)
            print(text)
            telegram_bot.send_message(chat_id=chat_id, parse_mode='html', text=text)
    except Exception:
        print(traceback.format_exc())
        if message:
            bot.reply_to(message, 'Failure'+traceback.format_exc())


def send_to_channel(data, message=None, telegram_bot=bot, channel_id=default_channel_id):
    try:
        if data['type'] == 'short' and data['media_files'] and len(data['media_files']) > 0:
            caption_text = data['text'] + '\n#' + data['category']
            media_group = media_files_packaging(data['media_files'], caption_text)
            telegram_bot.send_media_group(chat_id=channel_id, media=media_group)
        else:
            text = message_formatting(data)
            print(text)
            telegram_bot.send_message(chat_id=channel_id, parse_mode='html', text=text)
    except Exception:
        if message:
            bot.reply_to(message, 'Failure'+traceback.format_exc())
        print(traceback.format_exc())


def message_formatting(data):
    if data['type'] == 'short':
        if re.search(no_telegraph_regexp, data['aurl']):
            text = data['text'] + '\n#' + data['category']
        else:
            text = data['text'] + '\n#' + data['category']
    else:
        if re.search(no_telegraph_regexp, data['aurl']):
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
    return text


def media_files_packaging(media_files, caption=None):
    caption_text = caption
    media_group = []
    for media in media_files:
        if media['type'] == 'image':
            media_group.append(telebot.types.InputMediaPhoto(media['url'], caption=media['caption'], parse_mode='html'))
        elif media['type'] == 'video':
            media_group.append(telebot.types.InputMediaVideo(media['url'], caption=media['caption'], parse_mode='html'))
        elif media['type'] == 'audio':
            media_group.append(telebot.types.InputMediaAudio(media['url'], caption=media['caption'], parse_mode='html'))
    media_group[0].caption = caption_text
    return media_group

# bot.infinity_polling()
