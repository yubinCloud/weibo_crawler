from const import LOGGING
from lxml import etree

class FollowParser:
    """
    解析关注列表页
    """
    def __init__(self, follow_selector):
        self.selector = follow_selector

    def get_follows(self):
        """获取本页全部follow的信息"""
        follow_list = list()
        follow_nodes = self.selector.xpath(r'/html/body/table')
        for node in follow_nodes:
            a_follow = self.get_one_follow(node)
            if a_follow is not None:
                follow_list.append(a_follow)
        return follow_list


    def get_one_follow(self, follow_node):
        follow_node = follow_node.xpath('.//td')[1]
        follow_user = follow_node.xpath('./a')[0]
        user_name = follow_user.text  # 关注者的昵称
        user_id = follow_user.get('href')  # 关注者的id
        if type(user_id) is str:
            user_id = user_id[user_id.rfind(r'/') + 1: ]
        fans_num = follow_node.xpath('text()')  # 关注者的粉丝数
        if len(fans_num) != 0:
            # fans_num = str(fans_num[0])
            fans_num = int(fans_num[0][2: -1])
        else:
            fans_num = None
        return dict(user_id=user_id, user_name=user_name, fans_num=fans_num)


    def get_max_page_num(self):
        """
        获取总页数
        """
        total_page_num = ''.join(self.selector.xpath(r'//div[@id="pagelist"]/form/div/text()'))
        total_page_num = total_page_num[total_page_num.rfind(r'/') + 1: total_page_num.rfind('页')]
        return int(total_page_num)
