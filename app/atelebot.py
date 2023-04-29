import time

import telebot
import re
from .utils.util import *
from .api_functions import *

site_url = settings.env_var.get('SITE_URL', '127.0.0.1:' + settings.env_var.get('PORT', '1045'))
telebot_key = settings.env_var.get('TELEGRAM_BOT_KEY')
default_channel_name = settings.env_var.get('CHANNEL_ID', None)
youtube_api = settings.env_var.get('YOUTUBE_API', None)
image_size_limit = settings.env_var.get('IMAGE_SIZE_LIMIT', 1600)
telegram_text_limit = settings.env_var.get('TELEGRAM_TEXT_LIMIT', 1000)
allowed_users = settings.env_var.get('ALLOWED_USERS', '').split(',')
allowed_admin_users = settings.env_var.get('ALLOWED_ADMIN_USERS', '').split(',')
# initialize telebot
bot = telebot.TeleBot(telebot_key, num_threads=4)
default_channel_id = bot.get_chat(default_channel_name).id
url_pattern = re.compile(r'(http|https)://([\w.!@#$%^&*()_+-=])*\s*')  # 只摘取httpURL的pattern
http_parttern = '(http|https)://([\w.!@#$%^&*()_+-=])*\s*'
# no_telegraph_regexp="weibo\.com|m\.weibo\.cn|twitter\.com|zhihu\.com|douban\.com"
no_telegraph_regexp = "youtube\.com|bilibili\.com"
# no_telegraph_list = ['',]
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
        target_url = ''
        request_data = {'url': url}
        response_data = None
        if url.find('weibo.com') != -1 or url.find('m.weibo.cn') != -1:
            replying_message = bot.reply_to(message, '检测到微博URL，转化中\nWeibo URL detected, converting...')
            print('检测到微博URL，转化中\nWeibo URL detected, converting...')
            target_function = new_weibo_converter
        elif url.find('twitter.com') != -1:
            replying_message = bot.reply_to(message, '检测到TwitterURL，转化中\nTwitter URL detected, converting...')
            print('检测到TwitterURL，转化中\nTwitter URL detected, converting...')
            target_function = twitter_converter
            # target_url = twitterApiUrl
        elif url.find('zhihu.com') != -1:
            replying_message = bot.reply_to(message, '检测到知乎URL，转化中\nZhihu URL detected, converting...')
            print('检测到知乎URL，转化中\nZhihu URL detected, converting...')
            target_function = zhihu_converter
            # target_url = zhihuApiUrl
        elif url.find('douban.com') != -1:
            replying_message = bot.reply_to(message, '检测到豆瓣URL，转化中\nDouban URL detected, converting...')
            print('检测到豆瓣URL，转化中\nDouban URL detected, converting...')
            target_function = douban_converter
            # target_url = doubanApiUrl
        elif url.find('instagram.com') != -1:
            replying_message = bot.reply_to(message, '检测到InstagramURL，转化中\nInstagram URL detected, converting...')
            print('检测到InstagramURL，转化中\nInstagram URL detected, converting...')
            target_function = instagram_converter
        elif url.find('youtube.com') != -1:
            if not youtube_api:
                bot.reply_to(message,
                             '未配置YouTube API，无法抓取\nYouTube API is not configured. Cannot extract metadata from YouTube.')
            else:
                replying_message = bot.reply_to(message, '检测到YouTubeURL，转化中\nYouTube URL detected, converting...')
        else:
            if '_mastodon_session' in requests.utils.dict_from_cookiejar(get_response(url).cookies):
                replying_message = bot.reply_to(message, '检测到长毛象URL，转化中\nMustodon URL detected, converting...')
                print('检测到长毛象URL，转化中\nMustodon URL detected, converting...')
                # target_url = mustodonApiUrl
            else:
                bot.reply_to(message, '不符合规范，无法转化\ninvalid URL detected, cannot convert')
                print('不符合规范，无法转化\ninvalid URL detected, cannot convert')
                return False
        response_data = target_function(request_data)
        if response_data:
            data_id = str(uuid.uuid4())[:16]
            formatted_data[data_id] = response_data
        else:
            print('Failure')
            bot.reply_to(message, 'Failure')
            return
        if replying_message:
            bot.delete_message(message.chat.id, replying_message.message_id)
        # add function buttons
        if default_channel_name and str(message.from_user.id) in allowed_admin_users:
            forward_button_data = 'chan+' + str(message.id) + '+' + data_id + '+' + str(default_channel_name)
            forward_button = telebot.types.InlineKeyboardButton(text='发送到频道', callback_data=forward_button_data)
            print(forward_button.callback_data)
            func_buttons.append(forward_button)
        if 'media_files' in response_data:
            extract_button_data = 'extr+' + str(message.id) + '+' + data_id
            extract_button = telebot.types.InlineKeyboardButton(text='提取短文格式', callback_data=extract_button_data)
            func_buttons.append(extract_button)
        show_button_data = 'priv+' + str(message.id) + '+' + data_id
        show_button = telebot.types.InlineKeyboardButton(text='发送到私聊', callback_data=show_button_data)
        cancel_button_data = 'back+' + str(message.id)
        cancel_button = telebot.types.InlineKeyboardButton(text='取消', callback_data=cancel_button_data)
        basic_buttons = [cancel_button, show_button]
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
        message_id = call.data.split('+')[1]
        bot.answer_callback_query(call.id, "Sending message to channel")
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='正在把消息发送至绑定的频道……')
        if len(formatted_data) == 0:
            raise Exception('No data to send')
        the_data = formatted_data.pop(call.data.split('+')[2])
        send_formatted_message(data=the_data, message=call.message, chat_id=call.data.split('+')[3])
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
        message_id = call.data.split('+')[1]
        bot.answer_callback_query(call.id, "Message sent to private chat")
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='正在把摘取的内容发送至本对话……')
        if len(formatted_data) == 0:
            bot.reply_to(call.message, "No data to send")
            raise Exception('No data to send')
        the_data = formatted_data.pop(call.data.split('+')[2])
        send_formatted_message(data=the_data, message=call.message, chat_id=call.message.chat.id)
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
        message_id = call.data.split('+')[1]
        bot.answer_callback_query(call.id, "extracting...")
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='正在提取内容至 Telegram 消息……')
        if len(formatted_data) == 0:
            bot.reply_to(call.message, "No data to send")
            raise Exception('No data to send')
        the_data = formatted_data.pop(call.data.split('+')[2])
        the_data['type'] = 'short'
        if get_html_text_length(the_data['text']) > telegram_text_limit:
            short_text = the_data['text'][:(telegram_text_limit - len(the_data['turl']))]
            short_text = re.compile(r'<[^>]*?(?<!>)$').sub('', short_text)
            the_data['text'] = short_text + '...\n<a href="' + the_data['turl'] + '">阅读原文</a>'
        send_formatted_message(data=the_data, message=call.message, chat_id=call.message.chat.id)
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


# @bot.message_handler(func=lambda message: message.sender_chat.id == default_channel_id)
# def handle_message(message):
#     try:
#         latest_channel_message.append(message)
#     except Exception as e:
#         print(traceback.format_exc())
#         bot.reply_to(message, 'Failure' + traceback.format_exc())
#         return

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
    if data['type'] == 'short' or re.search(no_telegraph_regexp, data['aurl']):
        long_text = False
    else:
        long_text = True
    try:
        if not long_text and data['media_files'] and len(data['media_files']) > 0:
            caption_text = data['text'] + '\n#' + data['category']
            if data['media_files'] and len(data['media_files']) > 0:
                media_message_group, file_group = media_files_packaging(media_files=data['media_files'],
                                                                        caption=caption_text)
                if len(media_message_group) > 0:  # if there are some media groups to send, send it
                    for media_group in media_message_group:
                        sent_message = telegram_bot.send_media_group(chat_id=chat_id, media=media_group)
                    time.sleep(3)
                else:  # if there are no media groups to send, send the caption text and also note the message
                    sent_message = telegram_bot.send_message(chat_id=chat_id, parse_mode='html', text=caption_text)
                reply_to_message_id = None
                # if the chat is a channel, get the latest pinned message from the channel
                if discussion_chat_id != chat_id and len(media_message_group) > 0:
                    pinned_message = bot.get_chat(chat_id=discussion_chat_id).pinned_message
                    if pinned_message.forward_from_message_id == sent_message[-1].message_id:
                        reply_to_message_id = bot.get_chat(chat_id=discussion_chat_id).pinned_message.id \
                                            - len(sent_message)+1
                    else:
                        reply_to_message_id = bot.get_chat(chat_id=discussion_chat_id).pinned_message.id+1
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
            else:
                telegram_bot.send_message(chat_id=chat_id, parse_mode='html', text=caption_text)
        else:
            text = message_formatting(data)
            print(text)
            telegram_bot.send_message(chat_id=chat_id, parse_mode='html', text=text)
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
        io_object = download_a_iobytes_file(media['url'])
        file_size = io_object.size
        print('the size of this file is ' + str(file_size))
        if file_size > 50 * 1024 * 1024:  # if the size is over 50MB, skip this file
            continue
        print(io_object.name)
        if media['type'] == 'image':
            image_url = media['url']
            image = Image.open(io_object)
            img_width, img_height = image.size
            print(image_url, img_width, img_height)
            image = image_compressing(image, 2*image_size_limit)
            media_group.append(telebot.types.InputMediaPhoto(image, caption=media['caption'],
                                                             parse_mode='html'))
            print('will send ' + image_url + ' as a photo')
            if file_size > 5 * 1024 * 1024 or img_width > image_size_limit or img_height > image_size_limit:
                # if the size is over 5MB or dimension is larger than 1280 px, compress the image

                print('will also send ' + image_url + ' as a file')  # and also send it as a file
                io_object = download_a_iobytes_file(media['url'])
                if not io_object.name.endswith('.gif'):
                    file_group.append(io_object)
        elif media['type'] == 'gif':
            io_object = download_a_iobytes_file(media['url'], 'gif_image-' + str(media_counter) + '.gif')
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
