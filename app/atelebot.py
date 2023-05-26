import random
import telebot
import re
import time
import requests
import traceback
from .utils import util
from .utils import reply_messages
from . import api_functions
from .settings import env_var

site_url = env_var.get('SITE_URL', '127.0.0.1')
telebot_key = env_var.get('TELEGRAM_BOT_KEY')
default_channel_name = env_var.get('CHANNEL_ID', None)
youtube_api = env_var.get('YOUTUBE_API', None)
image_size_limit = env_var.get('IMAGE_SIZE_LIMIT', 1600)
telegram_text_limit = env_var.get('TELEGRAM_TEXT_LIMIT', 1000)
allowed_users = env_var.get('ALLOWED_USERS', '').split(',')
allowed_admin_users = env_var.get('ALLOWED_ADMIN_USERS', '').split(',')
# initialize telebot
bot = telebot.TeleBot(telebot_key, num_threads=4)
bot.delete_webhook()
print('webhook deleted')
if env_var.get('RUN_MODE', 'webhook') == 'webhook' and env_var.get('BOT', 'False') != 'True':
    bot.set_webhook(site_url + '/bot')
    print('webhook set')
default_channel_id = bot.get_chat(default_channel_name).id
url_pattern = re.compile(r'(http|https)://([\w.!@#$%^&*()_+-=])*\s*')  # 只摘取httpURL的pattern
http_parttern = r'(http|https)://([\w.!@#$%^&*()_+-=])*\s*'
douban_http_pattern = r'(http|https)://(www\.)+douban\.com'
no_telegraph_regexp = r"(youtube\.com)|(bilibili\.com\/video)"
formatted_data = {}
latest_channel_message = []


@bot.message_handler(regexp=http_parttern, chat_types=['private'])
def get_social_media(message):
    user_id = message.from_user.id
    print('user_id: ' + str(user_id) + ' is trying to convert a social media URL')
    if str(user_id) not in allowed_users:
        bot.reply_to(message, '你没有使用该bot的权限')
        return
    try:
        func_buttons = []
        basic_buttons = []
        url = url_pattern.search(message.text).group()
        print('the url is: ' + url)
        target_data = check_url_type(url, message)
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
        if default_channel_name and str(message.from_user.id) in allowed_admin_users:
            forward_button_data = 'chan+' + str(message.id) + '+' + data_id + '+' + str(default_channel_name)
            forward_button = telebot.types.InlineKeyboardButton(text='发送到频道', callback_data=forward_button_data)
            print(forward_button.callback_data)
            func_buttons.append(forward_button)
        extract_button_data = 'extr+' + str(message.id) + '+' + data_id
        extract_button = telebot.types.InlineKeyboardButton(text='强制直接提取', callback_data=extract_button_data)
        func_buttons.append(extract_button)
        if target_data['target_item_type'] == 'twitter':
            single_tweet_button_data = 'priv+' + str(message.id) + '+' + data_id + '+single'
            single_tweet_button = telebot.types.InlineKeyboardButton(text='单条推文',
                                                                     callback_data=single_tweet_button_data)
            func_buttons.append(single_tweet_button)
            thread_tweet_button_data = 'priv+' + str(message.id) + '+' + data_id + '+thread'
            thread_tweet_button = telebot.types.InlineKeyboardButton(text='获取推文串',
                                                                     callback_data=thread_tweet_button_data)
            func_buttons.append(thread_tweet_button)
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
    try:
        query_data = call.data.split('+')
        message_id = query_data[1]
        bot.answer_callback_query(call.id, "Sending message to channel")
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='社交媒体内容处理中……\nsocial media item processing...')
        if len(formatted_data) == 0:
            raise Exception('No data to send')
        target_data = formatted_data.pop(query_data[2])
        response_data = target_data['target_function'](target_data['url'])
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='处理完毕，正在把消息发送到频道……\nProcessing complete, sending message to channel...')
        send_formatted_message(data=response_data, message=call.message, chat_id=call.data.split('+')[3])
        bot.send_message(call.message.chat.id, reply_to_message_id=message_id, text='发送成功')
    except telebot.apihelper.ApiException as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure, timeout")
    except Exception as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure")
    finally:
        if call.message:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('priv'))
def callback_query(call):
    try:
        query_data = call.data.split('+')
        message_id = query_data[1]
        bot.answer_callback_query(call.id, "Message sent to private chat")
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='社交媒体内容处理中……\nsocial media item processing...')
        if len(formatted_data) == 0:
            bot.reply_to(call.message, "No data to send")
            raise Exception('No data to send')
        target_function_kwargs = {}
        target_data = formatted_data.pop(query_data[2])
        if target_data['target_item_type'] == 'twitter':
            if query_data[-1] == 'single':
                target_function_kwargs['scraper_type'] = 'single'
            elif query_data[-1] == 'thread':
                target_function_kwargs['scraper_type'] = 'thread'
        response_data = target_data['target_function'](target_data['url'], **target_function_kwargs)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='处理完毕，正在把消息发送至私聊……\nProcessing complete, sending message to private chat...')
        send_formatted_message(data=response_data, message=call.message, chat_id=call.message.chat.id)
        bot.send_message(call.message.chat.id, reply_to_message_id=message_id, text='摘取成功')
    except telebot.apihelper.ApiException as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure, timeout")
    except Exception as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure")
    finally:
        if call.message:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('extr'))
def callback_query(call):
    try:
        query_data = call.data.split('+')
        message_id = query_data[1]
        bot.answer_callback_query(call.id, "extracting...")
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='正在提取内容至 Telegram 消息……')
        if len(formatted_data) == 0:
            bot.reply_to(call.message, "No data to send")
            raise Exception('No data to send')
        target_data = formatted_data.pop(query_data[2])
        response_data = target_data['target_function'](target_data['url'])
        response_data['type'] = 'short'
        if util.get_html_text_length(response_data['text']) > telegram_text_limit:
            short_text = response_data['text'][:(telegram_text_limit - len(response_data['turl']))]
            short_text = re.compile(r'<[^>]*?(?<!>)$').sub('', short_text)
            response_data['text'] = short_text + '...\n<a href="' + response_data['turl'] + '">阅读原文</a>'
        send_formatted_message(data=response_data, message=call.message, chat_id=call.message.chat.id)
        bot.send_message(call.message.chat.id, reply_to_message_id=message_id, text='摘取成功')
    except telebot.apihelper.ApiException as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure, timeout")
    except Exception as e:
        print(traceback.format_exc())
        bot.answer_callback_query(call.id, "Failure")
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


@bot.message_handler(regexp=douban_http_pattern, chat_types=['group', 'supergroup'])
def handle_message(message):
    print('douban')
    try:
        url = url_pattern.search(message.text).group()
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
        if re.search(no_telegraph_regexp, data['aurl']) or data['type'] == 'long':
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
        if re.search(no_telegraph_regexp, data['aurl']):
            text = '<a href=\"' + data['aurl'] + '\"><b>' + data['title'] + '</b></a>\n'  'via #' + data['category'] + \
                   ' - <a href=\"' + data['originurl'] + ' \"> ' + data['origin'] + '</a>\n' + data['message']
        else:
            text = data['text'] + '\n#' + data['category']
    else:
        if re.search(no_telegraph_regexp, data['aurl']):
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
        io_object = util.download_a_iobytes_file(media['url'])
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
            image = util.image_compressing(image, 2 * image_size_limit)
            media_group.append(telebot.types.InputMediaPhoto(image, caption=media['caption'],
                                                             parse_mode='html'))
            print('will send ' + image_url + ' as a photo')
            if file_size > 5 * 1024 * 1024 or img_width > image_size_limit or img_height > image_size_limit:
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
    elif url.find('youtube.com') != -1:
        if not youtube_api:
            bot.reply_to(message,
                         '未配置YouTube API，无法抓取\nYouTube API is not configured. Cannot extract metadata from YouTube.')
        else:
            replying_message = bot.reply_to(message,
                                            '检测到YouTubeURL，预处理中……\nYouTube URL detected, preparing for processing....')
    else:
        if '_mastodon_session' in requests.utils.dict_from_cookiejar(util.get_response(url).cookies):
            replying_message = bot.reply_to(message,
                                            '检测到长毛象URL，预处理中……\nMustodon URL detected, preparing for processing....')
            print('检测到长毛象URL，预处理中……\nMustodon URL detected, preparing for processing....')
            # target_url = mustodonApiUrl
        else:
            replying_message = bot.reply_to(message, '不符合规范，无法转化\ninvalid URL detected, cannot convert')
            print('不符合规范，无法转化\ninvalid URL detected, cannot convert')
            return None, replying_message
    target_data = {'url': url, 'replying_message': replying_message, 'target_function': target_function,
                   'target_item_type': target_item_type}
    return target_data
