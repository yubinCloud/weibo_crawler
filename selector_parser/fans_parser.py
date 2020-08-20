from const import LOGGING
import utils


class FansParser:
    """
    解析粉丝列表页
    """
    def __init__(self, fans_selector):
        self.selector = fans_selector

    def get_fans(self):
        fans_list = list()
        fans_nodes = self.selector.xpath(r'//table')
        for node in fans_nodes:
            a_fans = self.get_one_fans(node)
            if a_fans is not None:
                fans_list.append(a_fans)
        return fans_list

    def get_one_fans(self, fans_node):
        return utils.extract_from_one_table_node(fans_node)


    def get_max_page_num(self):
        """
        获取总页数
        """
        total_page_num = ''.join(self.selector.xpath(r'//div[@id="pagelist"]/form/div/text()'))
        total_page_num = total_page_num[total_page_num.rfind(r'/') + 1: total_page_num.rfind('页')]
        return int(total_page_num)