import const
from tornado.httpclient import HTTPRequest
import enum

class BaseRequestBuilder:
    """用以根据参数构造出request的相关信息"""
    def __init__(self):
        self.url = str()
        self.proxy = const.PROXY

    def get_url(self):
        return self.url

    def make_request(self, method='GET',with_cookie=True, **req_kwargs):
        req = HTTPRequest(url=self.get_url(), method=method,
                          headers=const.get_headers(with_cookie=with_cookie),
                          request_timeout=const.REQUEST_TIME_OUT, **req_kwargs)
        return req


class UserIndexReqBuilder(BaseRequestBuilder):
    """根据用户id构造出用户的主页URL"""
    def __init__(self, user_id='1669879400'):
        super().__init__()
        self.url = 'https://weibo.cn/{}'.format(user_id)


class UserInfoReqBuilder(BaseRequestBuilder):
    """根据用户id构造出用户的信息页URL"""
    def __init__(self, user_id):
        super().__init__()
        self.url = 'https://weibo.cn/{}/info'.format(user_id)


class UserWeiboPageReqBuilder(BaseRequestBuilder):
    """根据用户id构造用户的某一页微博的URL"""
    def __init__(self, user_id, page_num=1):
        super().__init__()
        self.url = 'https://weibo.cn/{}?page={}'.format(user_id, page_num)


class WeiboCommentReqBuilder(BaseRequestBuilder):
    """根据weibo_id获取该微博的评论URL"""
    def __init__(self, weibo_id, page_num=1):
        super().__init__()
        self.url = 'https://weibo.cn/comment/{}?page={}'.format(weibo_id, page_num)


class MblogPicAllReqBuilder(BaseRequestBuilder):
    """微博所有图片的URL"""
    def __init__(self, weibo_id):
        super().__init__()
        self.url = 'https://weibo.cn/mblog/picAll/' + weibo_id + '?rl=1'


class FollowsReqBuilder(BaseRequestBuilder):
    """一个用户关注的人的URL"""
    def __init__(self, user_id, page_num):
        super().__init__()
        self.url = 'https://weibo.cn/{}/follow?page={}'.format(user_id, page_num)


class FansReqBuilder(BaseRequestBuilder):
    """一个用户的粉丝页的URL"""
    def __init__(self, user_id, page_num):
        super().__init__()
        self.url = 'https://weibo.cn/{}/fans?page={}'.format(user_id, page_num)


class SearchWeiboReqBuilder(BaseRequestBuilder):
    """用于搜索微博的页面URL"""
    def __init__(self, keyword, page_num, is_hot):
        super().__init__()
        search_type = r"xsort=hot" if is_hot else r"typeall=1&suball=1"
        self.url = 'https://s.weibo.com/weibo?q={}&{}&page={}'.format(keyword, search_type, page_num)
        

@enum.unique
class UserType(enum.Enum):
    """搜索用户时的用户类型限制"""
    NO_LIMIT = enum.auto()  # 无限制
    ORG_VIP = enum.auto()  # 机构认证
    PER_VIP = enum.auto()  # 个人认证
    ORDINARY = enum.auto()  # 普通用户

    @staticmethod
    def to_url(user_type):
        return {
            UserType.NO_LIMIT: '',
            UserType.ORG_VIP: '&auth=org_vip',
            UserType.PER_VIP: '&auth=per_vip',
            UserType.ORDINARY: '&auth=ord'
        }.get(user_type)


@enum.unique
class Gender(enum.Enum):
    """搜索用户时的性别限制"""
    NO_LIMIT = enum.auto()
    MAN = enum.auto()
    WOMAN = enum.auto()

    @staticmethod
    def to_url(gender):
        return {
            Gender.NO_LIMIT: '',
            Gender.MAN: '&gender=man',
            Gender.WOMAN: '&gender=woman'
        }.get(gender)


@enum.unique
class AgeLimit(enum.Enum):
    """搜索用户时的年龄限制"""
    NO_LIMIT = enum.auto()  # 不限年龄
    BELOW_18 = enum.auto()  # 18岁以下
    FROM_19_TO_22 = enum.auto()  # 19-22岁
    FROM_23_TO_29 = enum.auto()  # 23-29岁
    FROM_30_TO_39 = enum.auto()  # 30-39岁
    OVER_40 = enum.auto()  # 高于40岁

    @staticmethod
    def to_url(age_limit):
        return {
            AgeLimit.NO_LIMIT: '',
            AgeLimit.BELOW_18: '&age=18y',
            AgeLimit.FROM_19_TO_22: '&age=22y',
            AgeLimit.FROM_23_TO_29: '&age=29y',
            AgeLimit.FROM_30_TO_39: '&age=39y',
            AgeLimit.OVER_40: '&age=40y'
        }.get(age_limit)


class SearchUsersReqBuilder(BaseRequestBuilder):
    """用于搜索用户的页面URL"""

    def __init__(self, keyword, user_type=UserType.NO_LIMIT, gender=Gender.NO_LIMIT,
                 age_limit=AgeLimit.NO_LIMIT, page_num=1):
        """
        :param keyword: 搜索关键字
        :param user_type: 用户类型
        :param gender: 性别
        :param age_limit: 年龄限制
        :param page_num: 页数
        """
        super().__init__()
        query_str = ''.join({UserType.to_url(user_type), Gender.to_url(gender), AgeLimit.to_url(age_limit)})
        self.url = 'https://s.weibo.com/user?q={}&Refer=weibo_user{}page={}'.format(keyword, query_str, page_num)


if __name__ == '__main__':
    from tornado import gen
    from tornado import httpclient

    def f():
        http_client = httpclient.HTTPClient()
        try:
            req = UserIndexReqBuilder('1669879400').make_request()
            response = http_client.fetch(req)
            print(response.body.decode('utf8'))
        except Exception as e:
            print(e)

    f()





