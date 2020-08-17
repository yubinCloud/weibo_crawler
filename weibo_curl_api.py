import tornado.ioloop
from tornado import web,gen, httpserver
import tornado.options
from tornado.options import define, options

from selector_parser import *
import const
from tools import weibo_web_curl

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

        if user_id is None:
            self.write()

        idx_curl_result = yield weibo_web_curl('users_show', user_id=user_id)  # 爬取主页的结果

        if not idx_curl_result['error_code']:
            idxParser = IndexParser(user_id, idx_curl_result.get('selector'))  # 构建一个主页解析器
            user_id = idxParser.get_user_id()  # 获取到真正的user_id
            info_curl_result = yield weibo_web_curl('user_info', user_id=user_id)  # 爬取信息页的结果
            if not info_curl_result['error_code']:
                infoParser = InfoParser(info_curl_result.get('selector'))  # 信息页解析器
                user_info = infoParser.extract_user_info()
                user = idxParser.get_user(user_info)
                print(user.__dict__)

                success = const.SUCCESS.copy()
                success['data'] = {
                    'result': user.__dict__,
                    'cursor': ''
                }
                self.write(success)
            else:
                pass
        else:
            pass




class TestHandler(tornado.web.RequestHandler):
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