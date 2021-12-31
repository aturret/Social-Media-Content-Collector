from collections import OrderedDict

class Telegraph(object):
    def __init__(self):
        self.type = ''

    def add_item(self,item):
        citem = OrderedDict()
        citem[item['type']]=item

    def telegram_combination(self):
        return '1'