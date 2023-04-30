chougou_stickers = [
    'CAACAgUAAxkBAAIJrWRO90gsvIQEeQcxa0oTPEtcDP2kAAK_BAAC4UXJV8gS4LDMP2scLwQ',
    'CAACAgUAAxkBAAIJr2RO91-mgsfAyDO-_kILYq_DsxMOAAKaBwACfojIV3DtmXeAIXMuLwQ',
    'CAACAgUAAxkBAAIJsWRO92aqX_dMWVCBn4MiP911ifueAAKgBAACFEjQVy6hn3A-L6RBLwQ',
    'CAACAgUAAxkBAAIJs2RO920q9ofDz7Vmg7IutFLhwaDAAALABAAC2MPJV3_bl7_ItRVbLwQ',
    'CAACAgUAAxkBAAIJtWRO93HBJSZWrKhu1M_mhpEGMRj3AAKPBAACeQTIV2odHWSAsY-lLwQ',
    'CAACAgUAAxkBAAIJt2RO93aIont55FVz3SzM8DxWorrhAAKmBAAC4J_IV9ktThJwxgk6LwQ',
    'CAACAgUAAxkBAAIJuWRO94JYyckisHrMFfUf-UEbk9VrAAL0AwACLl7QV1p1Lmk6eJgVLwQ'
]
reply_texts = [
    '我只是一只小臭狗，嗷呜～',
    '大家好，我是臭狗狗',
    '呜呜呜，小臭狗做错了什么…',
    '呼……臭狗困咯',
    '臭狗狗走咯，再见啦～',
    '不是不是不是，我不是一条臭狗，我是一条小臭狗',
    '小臭狗爱你哟',
]
# combine reply_texts and chougou_stickers in the format of {'reply_text': '', 'sticker': ''}
reply_message_groups = []
for i in range(len(reply_texts)):
    reply_message = {'text': reply_texts[i], 'sticker': chougou_stickers[i]}
    reply_message_groups.append(reply_message)
