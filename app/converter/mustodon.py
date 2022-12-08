import json
import requests
from collections import OrderedDict
from lxml import etree
import sys
import re


class Mustodon(object):
    def __init__(self, url):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
            'Cookie': ''}
        self.url = url

    def get_toot(self):
        html = requests.get(self.url, headers=self.headers, verify=False).text
        print(html)

a = Mustodon('')