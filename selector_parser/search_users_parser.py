from const import LOGGING

class SearchUsersParser:
    """搜索用户页面的解析器"""
    def __init__(self, search_users_selector):
        self.selector = search_users_selector

    def parse_page(self):
        """解析网页"""
        try:
            user_list = self._get_all_user()
        except Exception as e:
            print(e)
            LOGGING.warning(e)
            user_list = None
        return user_list


    def _get_all_user(self):
        """获取全部用户信息"""
        user_list = list()
        user_nodes = self.selector.xpath('//div[@id="pl_user_feedList"]/div')
        for node in user_nodes:
            user = self._parse_one_user(node)
            print(user.__dict__)
            user_list.append(user.__dict__)
        return user_list




    def _parse_one_user(self, user_node):
        """解析单个用户的selector节点"""
        user = SearchUsersParser.User()
        info_selector = user_node.xpath('./div[@class="info"]')[0]
        headers = info_selector.xpath('./div[1]/a')

        if len(headers) > 2:  # 拥有头衔的情况
            for header_node in headers[1: -1]:
                title = header_node.get('title')
                if title is not None:
                    user.titles.append(title)

        user.id = headers[-1].get('uid')
        user.nickname = ''.join(headers[0].xpath(".//text()"))

        all_p_node = info_selector.xpath('./p')
        first_p = all_p_node[0]
        gender_info = first_p.xpath('./i')[0].get('class')
        user.gender = 0 if gender_info.rfind('female') != -1 else 1  # 0为女性，1位男性
        user.location = ''.join(first_p.xpath('./text()')).strip()

        footer = None
        other_p_nodes = list()
        for p_node in all_p_node:
            if p_node is first_p:
                continue
            elif len(p_node.xpath('./span')) == 3:
                footer = p_node
            else:
                other_p_nodes.append(p_node)

        if footer is not None:
            spans = footer.xpath('./span')
            user.following = spans[0].xpath('./a/text()')[0]
            user.followers = spans[1].xpath('./a/text()')[0]
            user.weibo_num = spans[2].xpath('./a/text()')[0]

        for node in other_p_nodes:
            info = ''.join(node.xpath('.//text()'))
            info_type = info[0: 2]

            if info_type == '教育':
                user.education = info
            elif info_type == '职业':
                user.work = info
            elif info_type == '简介':
                user.description = info
            elif info_type == '标签':
                user.tags = node.xpath('./a/text()')
            else:
                user.verified_reason = info

        return user

    class User():
        def __init__(self):
            self.id = ''  # 用户的id
            self.nickname = ''  # 昵称

            self.titles = list()  # 所拥有的头衔
            self.verified_reason = ''  # 认证原因
            self.gender = ''  # 性别
            self.location = ''  # 位置
            self.description = ''  # 简介
            self.tags = ''  # 标签

            self.education = ''  # 教育信息
            self.work = ''  # 工作信息
            self.weibo_num = 0  # 微博数
            self.following = 0  # 关注数
            self.followers = 0  # 粉丝数

        def __str__(self):
            """打印微博用户信息"""
            result = ''
            result += u'用户昵称: %s\n' % self.nickname
            result += u'用户id: %s\n' % self.id
            result += u'微博数: %d\n' % self.weibo_num
            result += u'关注数: %d\n' % self.following
            result += u'粉丝数: %d\n' % self.followers
            return result
