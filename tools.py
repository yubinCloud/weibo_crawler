from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from lxml import etree

import const
import req_builder

aim_to_builder = {
    'users_show': req_builder.UserIndexReqBuilder,
    'user_info': req_builder.UserInfoReqBuilder,
}


@gen.coroutine
def weibo_web_curl(curl_aim, retry_time=const.RETRY_TIME, **kwargs):
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
    req = builder(**kwargs).make_request()  # 获得 http request

    for epoch in range(retry_time):
        try:
            response = yield client.fetch(req)
            http_code = response.code
            if http_code == 200:
                return {'error_code': 0, 'selector': etree.HTML(response.body)}
            else:
                return {'error_code': 1, 'resp': response}
        except Exception as e:
            print(e)
            raise e
