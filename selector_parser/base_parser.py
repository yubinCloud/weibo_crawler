from lxml import etree
from tornado.httpclient import HTTPResponse


class BaseParser:
    def __init__(self, response):
        """保存response于属性中，同时将response转化成selector"""
        self.response = response
        if isinstance(response, HTTPResponse):
            self.selector = etree.HTML(self.response.body)
        else:
            self.selector = None

