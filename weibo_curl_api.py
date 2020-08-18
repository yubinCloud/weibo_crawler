import tornado.ioloop
from tornado import web,gen, httpserver
import tornado.options
from tornado.options import define, options

from selector_parser import *
import const
from tools import weibo_web_curl, curl_result_to_api_result
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


class UsersShow(BaseHandler):
    """
    API: 用户展示接口
    根据用户id搜索用户
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





class TestHandler(tornado.web.RequestHandler):
    """
    用来测试的接口
    """
    @gen.coroutine
    def get(self):
        result = yield weibo_web_curl("users_show")
        print(result['selector'])



if __name__ == '__main__':
    app = tornado.web.Application([
        (r"/weibo_curl/api/users_show", UsersShow),
    ])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()