import const
from tornado.httpclient import HTTPRequest

class RequestBuilder:
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


class UserIndexReqBuilder(RequestBuilder):
    """根据用户id构造出用户的主页URL"""
    def __init__(self, user_id='1669879400'):
        super().__init__()
        self.url = 'https://weibo.cn/{}'.format(user_id)


class UserInfoReqBuilder(RequestBuilder):
    """根据用户id构造出用户的信息页URL"""
    def __init__(self, user_id):
        super().__init__()
        self.url = 'https://weibo.cn/{}/info'.format(user_id)


class UserWeiboPageReqBuilder(RequestBuilder):
    """根据用户id构造用户的某一页微博的URL"""
    def __init__(self, user_id, page_num=1):
        super().__init__()
        self.url = 'https://weibo.cn/{}?page={}'.format(user_id, page_num)


class WeiboCommentReqBuilder(RequestBuilder):
    """根据weibo_id获取该微博的评论URL"""
    def __init__(self, weibo_id, page_num=1):
        super().__init__()
        self.url = 'https://weibo.cn/comment/{}?page={}'.format(weibo_id, page_num)


class MblogPicAllReqBuilder(RequestBuilder):
    """微博所有图片的URL"""
    def __init__(self, weibo_id):
        super().__init__()
        self.url = 'https://weibo.cn/mblog/picAll/' + weibo_id + '?rl=1'


class FollowsReqBuilder(RequestBuilder):
    """一个用户关注的人的URL"""
    def __init__(self, user_id, page_num):
        super().__init__()
        self.url = 'https://weibo.cn/{}/follow?page={}'.format(user_id, page_num)


class FansReqBuilder(RequestBuilder):
    """一个用户的粉丝页的URL"""
    def __init__(self, user_id, page_num):
        super().__init__()
        self.url = 'https://weibo.cn/{}/fans?page={}'.format(user_id, page_num)


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





