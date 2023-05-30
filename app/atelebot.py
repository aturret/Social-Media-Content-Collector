import os
import random
import re
import time
import requests
import traceback
import telebot
from .utils import util
from .utils import reply_messages
from .utils.customized_errors import *
from . import api_functions
from .settings import env_var

SITE_URL = env_var.get('SITE_URL', '127.0.0.1')
TELEBOT_KEY = env_var.get('TELEGRAM_BOT_KEY')
DEFAULT_CHANNEL_ID = env_var.get('CHANNEL_ID', None)
YOUTUBE_API = env_var.get('YOUTUBE_API', None)
IMAGE_SIZE_LIMIT = env_var.get('IMAGE_SIZE_LIMIT', 1600)
TELEGRAM_TEXT_LIMIT = env_var.get('TELEGRAM_TEXT_LIMIT', 1000)
ALLOWED_USERS = env_var.get('ALLOWED_USERS', '').split(',')
ALLOWED_ADMIN_USERS = env_var.get('ALLOWED_ADMIN_USERS', '').split(',')
TELEBOT_API_SERVER_PORT = env_var.get('TELEBOT_API_SERVER_PORT', None)
if TELEBOT_API_SERVER_PORT:
    telebot.apihelper.API_URL = 'http://localhost:' + TELEBOT_API_SERVER_PORT + '/bot{0}/{1}'
# initialize telebot
bot = telebot.TeleBot(TELEBOT_KEY, num_threads=4)
bot.delete_webhook()
print('webhook deleted')
if env_var.get('RUN_MODE', 'webhook') == 'webhook' and env_var.get('BOT', 'False') != 'True':
    bot.set_webhook(SITE_URL + '/bot', timeout=1200)
    print('webhook set')
DEFAULT_CHANNEL_ID = bot.get_chat(DEFAULT_CHANNEL_ID).id
URL_PATTERN = re.compile(r'(?:http|https)://[\w.!@#$%^&*()_+-=/?]*\??([^#\s]*)')  # 只摘取httpURL的pattern
HTTP_PATTERN_REGEXP = r'(http|https)://([\w.!@#$%^&*()_+-=])*\s*'
DOUBAN_HTTP_REGEXP = r'(http|https)://(www\.)+douban\.com'
NO_TELEGRAPH_REGEXP = r"(youtube\.com)|(bilibili\.com\/video)"
VIDEO_URL_REGEXP = r"(youtube\.com)|(bilibili\.com\/video)|(youtu\.be)|(b23\.tv)"
formatted_data = {}
latest_channel_message = []


@bot.message_handler(regexp=HTTP_PATTERN_REGEXP, chat_types=['private'])
def get_social_media(message):
    user_id = message.from_user.id
    print('user_id: ' + str(user_id) + ' is trying to convert a social media URL')
    if str(user_id) not in ALLOWED_USERS:
        bot.reply_to(message, '你没有使用该bot的权限')
        return
    try:
        func_buttons = []
        basic_buttons = []
        url = URL_PATTERN.search(message.text).group()
        print('the url is: ' + url)
        target_data = check_url_type(url, message)
        if target_data['target_item_type'] == 'invalid':
            return
        if target_data:
            data_id = str(util.uuid.uuid4())[:16]
            formatted_data[data_id] = target_data
        else:
            print('Failure')
            bot.reply_to(message, 'Failure')
            return
        if target_data['replying_message']:
            bot.delete_message(message.chat.id, target_data['replying_message'].message_id)
        # add function buttons
        if DEFAULT_CHANNEL_ID and str(message.from_user.id) in ALLOWED_ADMIN_USERS:
            forward_button_data = 'chan+' + str(message.id) + '+' + data_id + '+' + str(DEFAULT_CHANNEL_ID)
            forward_button = telebot.types.InlineKeyboardButton(text='发送到频道', callback_data=forward_button_data)
            print(forward_button.callback_data)
            func_buttons.append(forward_button)
        extract_button_data = 'extr+' + str(message.id) + '+' + data_id
        extract_button = telebot.types.InlineKeyboardButton(text='强制直接提取', callback_data=extract_button_data)
        basic_buttons.append(extract_button)
        if target_data['target_item_type'] == 'twitter':
            single_tweet_button_data = 'priv+' + str(message.id) + '+' + data_id + '+single'
            single_tweet_button = telebot.types.InlineKeyboardButton(text='单条推文',
                                                                     callback_data=single_tweet_button_data)
            func_buttons.append(single_tweet_button)
            thread_tweet_button_data = 'priv+' + str(message.id) + '+' + data_id + '+thread'
            thread_tweet_button = telebot.types.InlineKeyboardButton(text='推文串',
                                                                     callback_data=thread_tweet_button_data)
            func_buttons.append(thread_tweet_button)
        elif target_data['target_item_type'] == 'video':
            video_info_button_data = 'priv+' + str(message.id) + '+' + data_id + '+info'
            video_info_button = telebot.types.InlineKeyboardButton(text='视频信息',
                                                                   callback_data=video_info_button_data)
            func_buttons.append(video_info_button)
            video_download_button_data = 'priv+' + str(message.id) + '+' + data_id + '+down'
            video_download_button = telebot.types.InlineKeyboardButton(text='下载视频',
                                                                       callback_data=video_download_button_data)
            func_buttons.append(video_download_button)
            video_hd_download_button_data = 'priv+' + str(message.id) + '+' + data_id + '+dlhd'
            video_hd_download_button = telebot.types.InlineKeyboardButton(text='下载高清视频',
                                                                            callback_data=video_hd_download_button_data)
            func_buttons.append(video_hd_download_button)
        else:
            show_button_data = 'priv+' + str(message.id) + '+' + data_id
            show_button = telebot.types.InlineKeyboardButton(text='发送到私聊', callback_data=show_button_data)
            func_buttons.append(show_button)
        cancel_button_data = 'back+' + str(message.id)
        cancel_button = telebot.types.InlineKeyboardButton(text='取消', callback_data=cancel_button_data)
        basic_buttons.append(cancel_button)
        if len(func_buttons) > 0:
            markup = telebot.types.InlineKeyboardMarkup([func_buttons, basic_buttons])
        else:
            markup = telebot.types.InlineKeyboardMarkup([basic_buttons])
        bot.send_message(message.chat.id, "选择您想要的操作：", reply_markup=markup)
    except Exception as e:
        print(traceback.format_exc())
        bot.reply_to(message, 'Failure' + traceback.format_exc())
        return


@bot.callback_query_handler(func=lambda call: call.data.startswith('chan'))
def callback_query(call):
    query_data = call.data.split('+')
    message_id = query_data[1]
    try:
        bot.answer_callback_query(call.id, "Sending message to channel")
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='社交媒体内容处理中……\nsocial media item processing...')
        if len(formatted_data) == 0:
            raise Exception('No data to send')
        target_data = formatted_data.pop(query_data[2])
        target_function_kwargs = target_data['extra_kwargs']
        target_function_kwargs['channel'] = True
        response_data = target_data['target_function'](target_data['url'], **target_function_kwargs)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='处理完毕，正在把消息发送到频道……\nProcessing complete, sending message to channel...')
        send_formatted_message(data=response_data, message=call.message, chat_id=call.data.split('+')[3])
        bot.send_message(call.message.chat.id, reply_to_message_id=message_id, text='发送成功')
    except telebot.apihelper.ApiException as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure, timeout")
        bot.send_message(call.message.chat.id, reply_to_message_id=message_id, text='Failure, timeout')
    except NoItemFoundException as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure, no item found")
        bot.send_message(call.message.chat.id, reply_to_message_id=message_id, text='Failure, no item found')
    except Exception as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure")
        bot.send_message(call.message.chat.id, reply_to_message_id=message_id, text='Failure')
    finally:
        if call.message:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('priv'))
def callback_query(call):
    query_data = call.data.split('+')
    message_id = query_data[1]
    try:
        bot.answer_callback_query(call.id, "Message sent to private chat")
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='社交媒体内容处理中……\nsocial media item processing...')
        if len(formatted_data) == 0:
            bot.reply_to(call.message, "No data to send")
            raise Exception('No data to send')
        target_data = formatted_data.pop(query_data[2])
        target_function_kwargs = target_data['extra_kwargs']
        if target_data['target_item_type'] == 'twitter':
            if query_data[-1] == 'single':
                target_function_kwargs['scraper_type'] = 'single'
            elif query_data[-1] == 'thread':
                target_function_kwargs['scraper_type'] = 'thread'
        if target_data['target_item_type'] == 'video':
            if query_data[-1] == 'info':
                target_function_kwargs['download'] = False
            else:
                target_function_kwargs['download'] = True
                if query_data[-1] == 'dlhd':
                    target_function_kwargs['hd'] = True
        response_data = target_data['target_function'](target_data['url'], **target_function_kwargs)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='处理完毕，正在把消息发送至私聊……\nProcessing complete, sending message to private chat...')
        send_formatted_message(data=response_data, message=call.message, chat_id=call.message.chat.id)
        bot.send_message(call.message.chat.id, reply_to_message_id=message_id, text='摘取成功')
    except telebot.apihelper.ApiException as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure, timeout")
        bot.send_message(call.message.chat.id, reply_to_message_id=message_id, text='Failure, timeout')
    except NoItemFoundException as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure, no item found")
        bot.send_message(call.message.chat.id, reply_to_message_id=message_id, text='Failure, no item found')
    except Exception as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure")
        bot.send_message(call.message.chat.id, reply_to_message_id=message_id, text='Failure')
    finally:
        if call.message:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('extr'))
def callback_query(call):
    query_data = call.data.split('+')
    message_id = query_data[1]
    try:
        bot.answer_callback_query(call.id, "extracting...")
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='正在提取内容至 Telegram 消息……')
        if len(formatted_data) == 0:
            bot.reply_to(call.message, "No data to send")
            raise Exception('No data to send')
        target_data = formatted_data.pop(query_data[2])
        target_function_kwargs = target_data['extra_kwargs']
        response_data = target_data['target_function'](target_data['url'], **target_function_kwargs)
        response_data['type'] = 'short'
        if util.get_html_text_length(response_data['text']) > TELEGRAM_TEXT_LIMIT:
            short_text = response_data['text'][:(TELEGRAM_TEXT_LIMIT - len(response_data['turl']))]
            short_text = re.compile(r'<[^>]*?(?<!>)$').sub('', short_text)
            response_data['text'] = short_text + '...\n<a href="' + response_data['turl'] + '">阅读原文</a>'
        send_formatted_message(data=response_data, message=call.message, chat_id=call.message.chat.id)
        bot.send_message(call.message.chat.id, reply_to_message_id=message_id, text='摘取成功')
    except telebot.apihelper.ApiException as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure, timeout")
        bot.send_message(call.message.chat.id, reply_to_message_id=message_id, text='Failure, timeout')
    except NoItemFoundException as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure, no item found")
        bot.send_message(call.message.chat.id, reply_to_message_id=message_id, text='Failure, no item found')
    except Exception as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure")
        bot.send_message(call.message.chat.id, reply_to_message_id=message_id, text='Failure')
    finally:
        if call.message:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('back'))
def callback_query(call):
    try:
        bot.answer_callback_query(call.id, "cancel...")
    except:
        pass
    finally:
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.message_handler(chat_types=['private'], content_types=['sticker'])  # get sticker id
def handle_message(message):
    try:
        bot.reply_to(message, 'The sticker id is: ' + message.sticker.file_id)
    except Exception as e:
        print(traceback.format_exc())
        bot.reply_to(message, 'Failure' + traceback.format_exc())


@bot.message_handler(regexp=DOUBAN_HTTP_REGEXP, chat_types=['group', 'supergroup'])
def handle_message(message):
    print('douban')
    try:
        url = URL_PATTERN.search(message.text).group()
        print('the url is: ' + url)
        target_function, replying_message = check_url_type(url, message)
        request_data = {'url': url}
        response_data = target_function(request_data)
        if response_data:
            send_formatted_message(data=response_data, message=replying_message, chat_id=message.chat.id)
        bot.delete_message(chat_id=message.chat.id, message_id=replying_message.message_id)
    except Exception as e:
        print(traceback.format_exc())
        return


@bot.message_handler(commands=['hello'])  # a little Easter egg of responding to /hello with stickers
def handle_message(message):
    try:  # get a random number from the length of the list
        messages = reply_messages.reply_message_groups
        random_number = random.randint(0, len(messages) - 1)
        # reply to the message
        bot.send_sticker(message.chat.id, messages[random_number]['sticker'])
        bot.send_message(message.chat.id, messages[random_number]['text'])
    except Exception as e:
        print(traceback.format_exc())
        bot.reply_to(message, 'Failure' + traceback.format_exc())
        return


def send_formatted_message(data, message=None, chat_id=None, telegram_bot=bot):
    if (not chat_id) and message:
        chat_id = message.chat.id
    else:
        chat_id = bot.get_chat(chat_id=chat_id).id
    discussion_chat_id = chat_id
    the_chat = telegram_bot.get_chat(chat_id=chat_id)
    if the_chat.type == 'channel':
        if the_chat.linked_chat_id:
            discussion_chat_id = the_chat.linked_chat_id
    try:
        caption_text = data['text'] + '\n#' + data['category']
        if (re.search(NO_TELEGRAPH_REGEXP, data['aurl']) and data['category'] not in ['Bilibili', 'YouTube']) \
                or data['type'] == 'long':
            # if the url is not in the no_telegraph_list or the type is long, send long format message
            text = message_formatting(data)
            print(text)
            telegram_bot.send_message(chat_id=chat_id, parse_mode='html', text=text)
        elif data['type'] == 'short' and data['media_files'] and len(data['media_files']) > 0:
            # if the type is short and there are some media files, send media group
            media_message_group, file_group = media_files_packaging(media_files=data['media_files'],
                                                                    caption=caption_text)
            if len(media_message_group) > 0:  # if there are some media groups to send, send it
                for media_group in media_message_group:
                    sent_message = telegram_bot.send_media_group(chat_id=chat_id, media=media_group)
                time.sleep(3)
            else:  # if there are no media groups to send, send the caption text and also note the message
                sent_message = telegram_bot.send_message(chat_id=chat_id, parse_mode='html', text=caption_text)
            reply_to_message_id = None
            if discussion_chat_id != chat_id and len(media_message_group) > 0:
                # if the chat is a channel, get the latest pinned message from the channel
                pinned_message = bot.get_chat(chat_id=discussion_chat_id).pinned_message
                if pinned_message.forward_from_message_id == sent_message[-1].message_id:
                    reply_to_message_id = bot.get_chat(chat_id=discussion_chat_id).pinned_message.id \
                                          - len(sent_message) + 1
                else:
                    reply_to_message_id = bot.get_chat(chat_id=discussion_chat_id).pinned_message.id + 1
            if len(file_group) > 0:  # send files, the files messages should be replied to the message sent before
                telegram_bot.send_message(chat_id=discussion_chat_id, parse_mode='html',
                                          reply_to_message_id=reply_to_message_id,
                                          text='有部分图片超过尺寸或大小限制，以文件形式发送：')
                for file in file_group:
                    if file.name.endswith('.gif'):
                        print('sending gif')
                        telegram_bot.send_video(chat_id=discussion_chat_id,
                                                reply_to_message_id=reply_to_message_id, video=file)
                    else:
                        telegram_bot.send_document(chat_id=discussion_chat_id,
                                                   reply_to_message_id=reply_to_message_id, document=file)
        else:  # if there are no media files, send the caption text
            telegram_bot.send_message(chat_id=chat_id, parse_mode='html', text=caption_text)
    except Exception:
        print(traceback.format_exc())
        if message:
            bot.reply_to(message, 'Failure\n' + traceback.format_exc())


def message_formatting(data):
    if data['type'] == 'short':
        if re.search(NO_TELEGRAPH_REGEXP, data['aurl']) and data['category'] not in ['YouTube', 'Bilibili']:
            text = '<a href=\"' + data['aurl'] + '\"><b>' + data['title'] + '</b></a>\n'  'via #' + data['category'] + \
                   ' - <a href=\"' + data['originurl'] + ' \"> ' + data['origin'] + '</a>\n' + data['message']
        else:
            text = data['text'] + '\n#' + data['category']
    else:
        if re.search(NO_TELEGRAPH_REGEXP, data['aurl']) and data['category'] not in ['YouTube', 'Bilibili']:
            text = '<a href=\"' + data['aurl'] + '\">' '<b>' + data['title'] + '</b></a>\nvia #' + data['category'] + \
                   ' - <a href=\"' + data['originurl'] + ' \"> ' + data['origin'] + '</a>\n' + data['message']
        else:
            text = '<a href=\"' + data['turl'] + '\"><b>' + data['title'] + '</b></a>\nvia #' + data['category'] + \
                   ' - <a href=\"' + data['originurl'] + ' \"> ' + data['origin'] + '</a>\n' + data['message'] + \
                   '<a href=\"' + data['aurl'] + '\">阅读原文</a>'
    return text


def media_files_packaging(media_files, caption=None):
    caption_text = caption if caption else ''
    media_counter = file_counter = 0
    media_message_group = []
    media_group = []
    file_group = []
    for media in media_files:
        print('a new media file incoming...')
        if media_counter == 9:
            print('the number of valid media files is greater than 9, divide them into new groups')
            media_message_group.append(media_group)
            media_group = []
            media_counter = 0
        print('the ' + str((media_counter + 1)) + '\'s media: ' + media['type'] + ': ' + media['url'])
        # if the url if a network url, download it
        if media['url'].startswith('http'):
            io_object = util.download_a_iobytes_file(media['url'])
            if not TELEBOT_API_SERVER_PORT:
                file_size = io_object.size
                print('the size of this file is ' + str(file_size))
                if file_size > 50 * 1024 * 1024:  # if the size is over 50MB, skip this file
                    continue
            print(io_object.name)
            if media['type'] == 'image':
                image_url = media['url']
                image = util.Image.open(io_object)
                img_width, img_height = image.size
                print(image_url, img_width, img_height)
                image = util.image_compressing(image, 2 * IMAGE_SIZE_LIMIT)
                media_group.append(telebot.types.InputMediaPhoto(image, caption=media['caption'],
                                                                 parse_mode='html'))
                print('will send ' + image_url + ' as a photo')
                if file_size > 5 * 1024 * 1024 or img_width > IMAGE_SIZE_LIMIT or img_height > IMAGE_SIZE_LIMIT:
                    # if the size is over 5MB or dimension is larger than 1280 px, compress the image

                    print('will also send ' + image_url + ' as a file')  # and also send it as a file
                    io_object = util.download_a_iobytes_file(media['url'])
                    if not io_object.name.endswith('.gif'):
                        file_group.append(io_object)
            elif media['type'] == 'gif':
                io_object = util.download_a_iobytes_file(media['url'], 'gif_image-' + str(media_counter) + '.gif')
                io_object.name = io_object.name + '.gif'
                file_group.append(io_object)
            elif media['type'] == 'video':
                file_like_object = telebot.types.InputFile(io_object)
                media_group.append(telebot.types.InputMediaVideo(file_like_object, caption=media['caption'],
                                                                 parse_mode='html'))
            elif media['type'] == 'audio':
                file_like_object = telebot.types.InputFile(io_object)
                media_group.append(telebot.types.InputMediaAudio(file_like_object, caption=media['caption'],
                                                                 parse_mode='html'))
        else:  # the url is a local file string path
            if media['type'] == 'video':
                file_size = os.path.getsize(media['url'])
                if file_size > 50 * 1024 * 1024 and not TELEBOT_API_SERVER_PORT:  # if the size is over 50MB, skip this file
                    print('the size of this file is ' + str(file_size) + ', skip it')
                    continue
                if file_size > 2 * 1024 * 1024 * 1024 and TELEBOT_API_SERVER_PORT is not None:
                    print('the size of this file is ' + str(file_size) + ', skip it')
                    continue
                file_like_object = telebot.types.InputFile(media['url'])
                media_group.append(telebot.types.InputMediaVideo(file_like_object, caption=media['caption'],
                                                                 parse_mode='html'))
        media_counter += 1
    if len(media_message_group) == 0:
        if len(media_group) == 0:
            print('no valid media files')
            return media_message_group, file_group
        else:
            print('the number of valid media files is ' + str(len(media_group)) +
                  ' which is less than 9, send them in one media group')
            media_message_group.append(media_group)
    elif len(media_group) > 0:
        media_message_group.append(media_group)
    media_message_group[0][0].caption = caption_text
    print(media_message_group[0][0].caption)
    if len(media_message_group) > 1:
        for i in range(1, len(media_message_group)):
            media_message_group[i][0].caption = '接上 - 第' + str(i + 1) + '组媒体文件'
    return media_message_group, file_group


def check_url_type(url, message):
    extra_kwargs = {}
    if url.find('weibo.com') != -1 or url.find('m.weibo.cn') != -1:
        replying_message = bot.reply_to(message,
                                        '检测到微博URL，预处理中……\nWeibo URL detected, preparing for processing....')
        print('检测到微博URL，预处理中……\nWeibo URL detected, preparing for processing....')
        target_function = api_functions.new_weibo_converter
        target_item_type = 'weibo'
    elif url.find('twitter.com') != -1:
        replying_message = bot.reply_to(message,
                                        '检测到TwitterURL，预处理中……\nTwitter URL detected, preparing for processing....')
        print('检测到TwitterURL，预处理中……\nTwitter URL detected, preparing for processing....')
        target_function = api_functions.twitter_converter
        target_item_type = 'twitter'
        # target_url = twitterApiUrl
    elif url.find('zhihu.com') != -1:
        replying_message = bot.reply_to(message,
                                        '检测到知乎URL，预处理中……\nZhihu URL detected, preparing for processing....')
        print('检测到知乎URL，预处理中……\nZhihu URL detected, preparing for processing....')
        target_function = api_functions.zhihu_converter
        target_item_type = 'zhihu'
    elif url.find('douban.com') != -1:
        replying_message = bot.reply_to(message,
                                        '检测到豆瓣URL，预处理中……\nDouban URL detected, preparing for processing....')
        print('检测到豆瓣URL，预处理中……\nDouban URL detected, preparing for processing....')
        target_function = api_functions.douban_converter
        target_item_type = 'douban'
    elif url.find('instagram.com') != -1:
        replying_message = bot.reply_to(message,
                                        '检测到InstagramURL，预处理中……\nInstagram URL detected, preparing for processing....')
        print('检测到InstagramURL，预处理中……\nInstagram URL detected, preparing for processing....')
        target_function = api_functions.instagram_converter
        target_item_type = 'instagram'
    elif re.search(VIDEO_URL_REGEXP, url) is not None:
        if url.find('youtube.com') != -1 or url.find('youtu.be') != -1:
            replying_message = bot.reply_to(message,
                                            '检测到YouTubeURL，预处理中……\nYouTube URL detected, preparing for processing....')
            extra_kwargs['file_download'] = True
        elif url.find('bilibili.com') != -1:
            replying_message = bot.reply_to(message,
                                            '检测到BilibiliURL，预处理中……\nBilibili URL detected, preparing for processing....')
        target_function = api_functions.video_converter
        target_item_type = 'video'
    else:
        if '_mastodon_session' in requests.utils.dict_from_cookiejar(util.get_response(url).cookies):
            replying_message = bot.reply_to(message,
                                            '检测到长毛象URL，预处理中……\nMustodon URL detected, preparing for processing....')
            print('检测到长毛象URL，预处理中……\nMustodon URL detected, preparing for processing....')
        else:
            replying_message = bot.reply_to(message, '不符合规范，无法转化\ninvalid URL detected, cannot convert')
            print('不符合规范，无法转化\ninvalid URL detected, cannot convert')
            target_function = None
            target_item_type = 'invalid'
    target_data = {'url': url, 'replying_message': replying_message, 'target_function': target_function,
                   'target_item_type': target_item_type, 'extra_kwargs': extra_kwargs}
    return target_data
