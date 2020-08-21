from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPError
from lxml import etree
from enum import Enum, auto, unique

import const
import req_builder
from weibo_curl_error import WeiboCurlError


@unique  # 确保枚举值唯一
class Aim(Enum):
    """枚举全部爬取目标"""
    users_show = auto()
    users_info = auto()
    users_weibo_page = auto()
    weibo_comment = auto()
    mblog_pic_all = auto()
    follow = auto()
    fans = auto()
    search_weibo = auto()


aim_to_builder = {  # 将爬取目标对应到相符合的请求构造器
    Aim.users_show: req_builder.UserIndexReqBuilder,
    Aim.users_info: req_builder.UserInfoReqBuilder,
    Aim.users_weibo_page: req_builder.UserWeiboPageReqBuilder,
    Aim.weibo_comment: req_builder.WeiboCommentReqBuilder,
    Aim.mblog_pic_all: req_builder.MblogPicAllReqBuilder,
    Aim.follow: req_builder.FollowsReqBuilder,
    Aim.fans: req_builder.FansReqBuilder,
    Aim.search_weibo: req_builder.SearchWeiboReqBuilder,
}


@gen.coroutine
def weibo_web_curl(curl_aim, retry_time=const.RETRY_TIME, with_cookie=True, **kwargs):
    """
    根据爬取的目标对相对应的网站发送request请求并获得response
    :param curl_aim: 爬取的目标，其值必须为Aim枚举值
    :param retry_time: 最多尝试发送request的次数
    :param kwargs: 需要转发给RequestBuilder的初始化参数
    :return: 当参数use_bs4为True时返回bs4解析的soup，False时返回etree解析后的selector
    """
    global response
    client = AsyncHTTPClient()
    builder = aim_to_builder.get(curl_aim)

    for epoch in range(retry_time):
        req = builder(**kwargs).make_request(with_cookie=with_cookie)  # 获得 http request
        try:
            response = yield client.fetch(req)
        except HTTPError as e:
            const.LOGGING.warning('A HTTPError occurred:{} [{}, {}]'.format(e, curl_aim, kwargs))
            if e.get('code') == 403 or e.get('code') == 404:
                return {'error_code': 2, 'errmsg': "Can't find page: {}".format(req.url)}
            elif e.get('code') == 559:  # 超时错误
                pass  # 再次通过builder构造request时会重新获得proxy
            continue

        http_code = response.code
        if http_code == 200:
            print(response.body.decode('utf8'))
            return {'error_code': 0, 'selector': etree.HTML(response.body)}
        else:
            return {'error_code': 1, 'errmsg': 'Sina return a Abnormal http status code: {}'.format(http_code)}


def curl_result_to_api_result(curl_result):
    """
    将 weibo_web_curl 返回的错误结果进行处理获得对应的错误信息
    """
    error_res = None
    errcode = curl_result.get('error_code')
    if errcode == 1:
        error_res = WeiboCurlError.OTHER_RESP_ERROR.copy()
        error_res['error_msg'] = curl_result.get('errmsg')
    elif errcode == 2:
        error_res = WeiboCurlError.URL_ARGS_ERROR.copy()
        error_res['error_msg'] += curl_result.get('errmsg')
    return error_res