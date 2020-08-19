import tornado.ioloop
from tornado import web,gen, httpserver
import tornado.options
from tornado.options import define, options

from selector_parser import *
import const
from web_curl import weibo_web_curl, curl_result_to_api_result
from weibo_curl_error import WeiboCurlError

define("port", default=8000, help="run on the given port", type=int)


class BaseHandler(tornado.web.RequestHandler):
    def args2dict(self):
        """
        将请求url中的请求查询字符串转化成dict
        :return: 转化后的dict
        """
        input_dict = dict()
        args = self.request.arguments
        for i in args:
            input_dict[i] = self.get_argument(i)
        return input_dict


class UsersShowHandler(BaseHandler):
    """
    API: 用户展示接口：根据用户id搜索用户
    routing path: /weibo_curl/api/users_show
    """
    @gen.coroutine
    def get(self):
        args_dict = self.args2dict()
        user_id = args_dict.get('user_id')
        if user_id is None:  # 此时URL缺少查询参数
            self.write(WeiboCurlError.URL_LACK_ARGS)
            return

        task_finished = False  # 标志此次处理任务是否完成
        while not task_finished:
            try:
                idx_curl_result = yield weibo_web_curl('users_show', user_id=user_id)  # 爬取主页的结果
                if not idx_curl_result['error_code']:  # 如果主页http响应的状态码为200，则继续进行
                    idxParser = IndexParser(user_id, idx_curl_result.get('selector'))  # 构建一个主页解析器
                    user_id = idxParser.get_user_id()  # 获取到真正的user_id

                    info_curl_result = yield weibo_web_curl('user_info', user_id=user_id)  # 爬取信息页的结果
                    if not info_curl_result['error_code']:
                        infoParser = InfoParser(info_curl_result.get('selector'))  # 信息页解析器
                        user_info = infoParser.extract_user_info()
                        user = idxParser.get_user(user_info)
                        print(user.__dict__)

                        success = const.SUCCESS.copy()
                        try:
                            success['data'] = {
                                'result': user.__dict__,
                                'cursor': ''
                            }
                        except AttributeError:  # user没有__dict__属性时，说明未爬取到user
                            self.write(WeiboCurlError.URL_ARGS_ERROR)  # 报告参数错误
                            return
                        self.write(success)
                        return
                    else:
                        error_res = curl_result_to_api_result(info_curl_result)
                        self.write(error_res)
                        return
                else:
                    error_res = curl_result_to_api_result(idx_curl_result)
                    self.write(error_res)
                    return

            except CookieInvalidException:  # Cookie无效，更新Cookie后重新开始任务
                const.update_cookie()
                continue
            except Exception as e:
                const.LOGGING.error(e)


class UserTimelineHandler(BaseHandler):
    """
    API: 用户时间线接口
    根据用户id搜索用户的微博
    route: /weibo_curl/api/statuses_user_timeline
    """
    @gen.coroutine
    def get(self):
        args_dict = self.args2dict()
        user_id = args_dict.get('user_id')
        if user_id is None:  # 此时缺少参数
            self.write(WeiboCurlError.URL_LACK_ARGS)
            return
        cursor = args_dict.get('cursor')
        if cursor is None:
            cursor = 1
        else:
            cursor = int(cursor)
        filter = args_dict.get('filter')
        if filter is None:
            filter = 0  # 默认爬取全部微博（原创+转发）

        page_curl_result = yield weibo_web_curl('user_weibo_page', user_id=user_id, page_num=cursor)
        pageParser = None
        if not page_curl_result['error_code']:
            pageParser = PageParser(user_id, page_curl_result['selector'], filter)
        weibos, weibo_id_list = pageParser.get_one_page([])

        for weibo in weibos:
            print(weibo.__dict__)

        print(weibo_id_list)



class TestHandler(tornado.web.RequestHandler):
    """
    用来测试的接口
    """
    @gen.coroutine
    def get(self):
        result = yield weibo_web_curl("users_show")
        print(result['selector'])



if __name__ == '__main__':
    ROUTE_PREFIX = r"/weibo_curl/api/"  # 路由前缀

    app = tornado.web.Application([
        (ROUTE_PREFIX + r"users_show", UsersShowHandler),
        (ROUTE_PREFIX + r"statuses_user_timeline", UserTimelineHandler)
    ])

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()