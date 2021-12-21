from util import handle_garbled, handle_html
from time import sleep
import random


class Weibo:
    def __init__(self,url):
        self.url = url
        self.selector = ""

    def getContent(self):
        """获取长原创微博"""
        self.selector = handle_html(url=self.url)
        print(self.selector)
        if self.selector is not None:
            info = self.selector.xpath("//div[@class='weibo-text']")
            wb_content = handle_garbled(info)
            print(len(info))
            return wb_content
            # wb_time = info.xpath("//span[@class='time']")
            # weibo_content = wb_content[wb_content.find(':') +
            #                            1:wb_content.rfind(wb_time)]
            # if weibo_content is not None:
            #     return weibo_content
        # try:
        #     # for i in range(5):
        #     self.selector = handle_html(self.url)
        #     print(self.selector)
        #     if self.selector is not None:
        #         info = self.selector.xpath("//div[@class='weibo-text']")[1]
        #         wb_content = handle_garbled(info)
        #         wb_time = info.xpath("//span[@class='time']")[0]
        #         weibo_content = wb_content[wb_content.find(':') +
        #                                    1:wb_content.rfind(wb_time)]
        #         if weibo_content is not None:
        #             return weibo_content
        #         # sleep(random.randint(6, 10))
        # except Exception:
        #     print(u'网络出错')

w = Weibo(url='https://m.weibo.cn/1793285524/4716452411869606')
w.getContent()