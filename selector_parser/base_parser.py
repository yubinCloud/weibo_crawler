from lxml import etree

class BaseParser:
    def __init__(self, response):
        """保存response于属性中，同时将response转化成selector"""
        self.response = response
        self.selector = etree.HTML(self.response.body)

