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
    users_show = req_builder.UserIndexReqBuilder
    users_info = req_builder.UserInfoReqBuilder
    users_weibo_page = req_builder.UserWeiboPageReqBuilder
    weibo_comment = req_builder.WeiboCommentReqBuilder
    mblog_pic_all = req_builder.MblogPicAllReqBuilder
    follow = req_builder.FollowsReqBuilder
    fans = req_builder.FansReqBuilder
    search_weibo = req_builder.SearchWeiboReqBuilder
    search_users = req_builder.SearchUsersReqBuilder


@gen.coroutine
def weibo_web_curl(curl_aim: Aim, retry_time=const.RETRY_TIME, with_cookie=True, **kwargs):
    """
    根据爬取的目标对相对应的网站发送request请求并获得response
    :param curl_aim: 爬取的目标，其值必须为Aim枚举值
    :param retry_time: 最多尝试发送request的次数
    :param kwargs: 需要转发给RequestBuilder的初始化参数
    :return: 当参数use_bs4为True时返回bs4解析的soup，False时返回etree解析后的selector
    """
    global response
    client = AsyncHTTPClient()
    builder = curl_aim.value


    for epoch in range(retry_time):
        req = builder(**kwargs).make_request(with_cookie=with_cookie)  # 获得 http request

        try:
            response = yield client.fetch(req)
        except HTTPError as e:
            const.LOGGING.warning('A HTTPError occurred:{} [{}, {}]'.format(e, curl_aim, kwargs))
            if e.get('code') == 404:
                return {'error_code': 2, 'errmsg': "Can't find page: {}".format(req.url)}
            elif e.get('code') == 559:  # 超时错误
                pass  # 再次通过builder构造request时会重新获得proxy
                continue
            else:
                print('test')

        http_code = response.code
        if http_code == 200:
            return {'error_code': 0, 'selector': etree.HTML(response.body)}
        elif http_code == 302 or http_code == 403:  # Cookie 失效
            return {'error_code': 3, 'errmsg': 'Invalid cookie: {}'.format(req.headers.get('Cookie'))}
        elif http_code == 418:  # ip失效，偶尔产生，需要再次请求
            return {'error_code': 4, 'errmsg': 'Please change a proxy and send a request again'}
        else:
            return {'error_code': 1, 'errmsg': 'Http status code: {}'.format(http_code)}


def curl_result_to_api_result(curl_result):
    """
    将 weibo_web_curl 返回的错误结果进行处理获得对应的错误信息
    """
    error_code = curl_result.get('error_code')

    if error_code == 1:
        error_res = WeiboCurlError.ABNORMAL_HTTP_CODE.copy()
        error_res['error_msg'] += curl_result.get('errmsg')
    elif error_code == 2:
        error_res = WeiboCurlError.URL_ARGS_ERROR.copy()
        error_res['error_msg'] += curl_result.get('errmsg')
    elif error_code == 3:
        error_res = WeiboCurlError.COOKIE_INVALID.copy()
        error_res['error_msg'] += curl_result.get('errmsg')
    elif error_code == 4:
        error_res = WeiboCurlError.IP_INVALID.copy()
        error_res['error_msg'] += curl_result.get('errmsg')
    else:
        error_res = WeiboCurlError.UNKNOWN_ERROR.copy()

    return error_res