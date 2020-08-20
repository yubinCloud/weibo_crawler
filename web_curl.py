from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPError
from lxml import etree

import const
import req_builder
from weibo_curl_error import WeiboCurlError

aim_to_builder = {
    'users_show': req_builder.UserIndexReqBuilder,
    'user_info': req_builder.UserInfoReqBuilder,
    'user_weibo_page': req_builder.UserWeiboPageReqBuilder,
    'weibo_comment': req_builder.WeiboCommentReqBuilder,
    'mblog_pic_all': req_builder.MblogPicAllReqBuilder,
}


@gen.coroutine
def weibo_web_curl(curl_aim, retry_time=const.RETRY_TIME, with_cookie=True, **kwargs):
    """
    根据爬取的目标对相对应的网站发送request请求并获得response
    :param curl_aim: 爬取的目标，其值必须为aim_to_builder的keys之一
    :param retry_time: 最多尝试发送request的次数
    :param kwargs: 需要转发给RequestBuilder的初始化参数
    :return:
    """
    global response
    assert curl_aim in aim_to_builder.keys()  # 保证 curl_aim 属于 aim_to_builder.keys()
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