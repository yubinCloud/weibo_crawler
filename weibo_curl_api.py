import tornado.ioloop
from tornado import web,gen, httpserver
import tornado.options
from tornado.options import define, options

from selector_parser import *
import const
from selector_parser import CommentParser
from web_curl import Aim, weibo_web_curl, curl_result_to_api_result
from weibo_curl_error import WeiboCurlError, CookieInvalidException
from req_builder import UserType, Gender, AgeLimit

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
                idx_curl_result = yield weibo_web_curl(Aim.users_show, user_id=user_id)  # 爬取主页的结果
                if not idx_curl_result['error_code']:  # 如果主页http响应的状态码为200，则继续进行
                    idxParser = IndexParser(user_id, idx_curl_result.get('selector'))  # 构建一个主页解析器
                    user_id = idxParser.get_user_id()  # 获取到真正的user_id

                    info_curl_result = yield weibo_web_curl(Aim.users_info, user_id=user_id)  # 爬取信息页的结果
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
        cursor = args_dict.get('cursor', '1')
        try:
            cursor = 1 if not cursor else int(cursor)
        except ValueError:
            self.write(WeiboCurlError.URL_ARGS_ERROR)
            return
        filter = args_dict.get('filter', 0)  # 默认爬取全部微博（原创+转发）

        page_curl_result = yield weibo_web_curl(Aim.users_weibo_page, user_id=user_id, page_num=cursor)
        pageParser = None
        if not page_curl_result['error_code']:
            pageParser = PageParser(user_id, page_curl_result['selector'], filter)
        else:
            error_res = curl_result_to_api_result(page_curl_result)
            self.write(error_res)
            return
        weibos, weibo_id_list = yield pageParser.get_one_page()

        for weibo in weibos:
            print(weibo.__dict__)

        print(weibo_id_list)

        success = const.SUCCESS.copy()
        try:
            success['data'] = {
                'result': [weibo.__dict__ for weibo in weibos],
                'cursor': str(cursor + 1)
            }
        except AttributeError:  # user没有__dict__属性时，说明未爬取到user
            self.write(WeiboCurlError.URL_ARGS_ERROR)  # 报告参数错误
            return
        self.write(success)
        return


class StatusesShowHandler(BaseHandler):
    """
    推文展示接口
    说明：根据推文id搜索推文
    路由：/weibo_curl/api/statuses_show
    """
    @gen.coroutine
    def get(self):
        args_dict = self.args2dict()
        weibo_id = args_dict.get('weibo_id')
        if weibo_id is None:
            self.write(WeiboCurlError.URL_LACK_ARGS)
            return

        comment_curl_result = yield weibo_web_curl(Aim.weibo_comment, weibo_id=weibo_id)
        if not comment_curl_result['error_code']:
            self.selector = comment_curl_result['selector']
        else:
            error_res = curl_result_to_api_result(comment_curl_result)
            self.write(error_res)
            return

        commonParser = CommentParser(weibo_id, selector=self.selector)

        try:
            is_original = commonParser.is_original()
            if is_original:
                weibo_content = yield commonParser.get_long_weibo()
            else:
                weibo_content = yield commonParser.get_long_retweet(rev_type=dict)

            user_id, user_name = commonParser.get_user()

            success = const.SUCCESS.copy()
            success['data'] = {
                'result': {
                    'weibo_id': weibo_id,
                    'user_id': user_id,
                    'user_name': user_name,
                    'original': is_original,
                    'weibo_content': weibo_content
                },
                'cursor': ''
            }
            print(success)
            self.write(success)
            return
        except Exception as e:
            self.write(WeiboCurlError.UNKNOWN_ERROR)
            const.LOGGING.error(e)


class FriendsHandler(BaseHandler):
    """
    用户朋友列表接口(朋友指关注的人)
        说明：根据用户id搜索用户朋友，同时也要返回他们的信息
        路由：/weibo_curl/api/friends_list
    """
    @gen.coroutine
    def get(self):
        # 获取查询参数
        args_dict = self.args2dict()
        user_id, cursor = args_dict.get('user_id'), args_dict.get('cursor', '1')
        if user_id is None:
            self.write(WeiboCurlError.URL_LACK_ARGS)
            return
        try:
            cursor = 1 if not cursor else int(cursor)
        except ValueError:
            self.write(WeiboCurlError.URL_ARGS_ERROR)
            return
        # 进行爬取
        follow_curl_result = yield weibo_web_curl(Aim.follow, user_id=user_id, page_num=cursor)
        if not follow_curl_result['error_code']:
            self.selector = follow_curl_result['selector']
        else:
            error_res = curl_result_to_api_result(follow_curl_result)
            self.write(error_res)
            return
        # 构建解析器
        followParser = FollowParser(self.selector)
        # 提取相关信息并返回结果
        try:
            follow_list = followParser.get_follows()  # 关注者的列表
            max_page_num = followParser.get_max_page_num()  # 总页数
            if cursor < max_page_num:
                cursor = str(cursor + 1)
            success = const.SUCCESS.copy()
            success['data'] = {
                'result': {
                    'friend_list': follow_list,
                    'max_page_num': max_page_num
                },
                'cursor': cursor
            }
            print(success)
            self.write(success)
            return
        except Exception as e:
            const.LOGGING.error(e)
            print(e)


class FollowersHandler(BaseHandler):
    """
    用户粉丝列表接口
        说明：根据用户id搜索用户粉丝
        路由：/weibo_curl/api/followers_list
    """
    @gen.coroutine
    def get(self):
        args_dict = self.args2dict()
        user_id, cursor = args_dict.get('user_id'), args_dict.get('cursor', '1')
        if user_id is None:
            self.write(WeiboCurlError.URL_LACK_ARGS)
            return
        try:
            cursor = 1 if cursor == 0 else int(cursor)
        except ValueError:  # 当对cursor转换产生错误时
            self.write(WeiboCurlError.URL_ARGS_ERROR)
            return
        # 进行爬取
        fans_curl_result = yield weibo_web_curl(Aim.fans, user_id=user_id, page_num=cursor)
        if not fans_curl_result['error_code']:
            self.selector = fans_curl_result['selector']
        else:
            error_res = curl_result_to_api_result(fans_curl_result)
            self.write(error_res)
            return
        # 构建解析器
        fansParser = FansParser(self.selector)
        # 提取相关信息并返回结果
        try:
            fans_list = fansParser.get_fans()
            max_page_num = fansParser.get_max_page_num()
            if cursor < max_page_num:
                cursor = str(cursor + 1)
            success = const.SUCCESS.copy()
            success['data'] = {
                'result': {
                    'friend_list': fans_list,
                    'max_page_num': max_page_num
                },
                'cursor': cursor
            }
            print(success)
            self.write(success)
            return
        except Exception as e:
            const.LOGGING.error(e)
            print(e)


class SearchTweetsHandler(BaseHandler):
    """
    推文搜索接口
        说明：根据关键词搜索推文
        路由：/weibo_curl/api/search_tweets
    """
    @gen.coroutine
    def get(self):
        # 获取参数
        args_dict = self.args2dict()
        keyword, cursor, is_hot = args_dict.get('keyword'), args_dict.get('cursor', '1'), args_dict.get('is_hot', False)
        if keyword is None:
            self.write(WeiboCurlError.URL_LACK_ARGS)  # 缺少参数
            return
        try:
            cursor = 1 if not cursor else int(cursor)
        except ValueError:
            self.write(WeiboCurlError.URL_ARGS_ERROR)
            return
        # 进行爬取
        search_weibo_curl_result = yield weibo_web_curl(Aim.search_weibo,
                                                        keyword=keyword, page_num=cursor, is_hot=is_hot)
        if not search_weibo_curl_result['error_code']:
            self.selector = search_weibo_curl_result['selector']
        else:
            error_res = curl_result_to_api_result(search_weibo_curl_result)
            self.write(error_res)
            return
        # 构建解析器
        searchWeiboParser = SearchWeiboParser(self.selector)
        # 获取微博信息
        weibo_list = searchWeiboParser.parse_page()
        if weibo_list is None:
            self.write(WeiboCurlError.PAGE_NOT_FOUND)  # 页面找不到
            return
        # 成功返回结果
        success = const.SUCCESS.copy()
        success['data'] = {
            'result': weibo_list,
            'cursor': str(cursor + 1)
        }
        self.write(success)
        return



class SearchUsersHandler(BaseHandler):
    """
    用户搜索接口
        说明：根据关键词搜索用户
        路由：/weibo_curl/api/users_search
    """
    @gen.coroutine
    def get(self):
        # 获取参数
        args_dict = self.args2dict()
        keyword, cursor = args_dict.get('keyword'), args_dict.get('cursor', '1')
        if keyword is None:
            self.write(WeiboCurlError.URL_LACK_ARGS)  # 缺少参数
            return
        try:
            cursor = 1 if not cursor else int(cursor)
        except ValueError:
            self.write(WeiboCurlError.URL_ARGS_ERROR)
            return
        user_type, gender, age_limit = args_dict.get('user_type'), args_dict.get('gender'), args_dict.get('age_limit')
        # 进行爬取
        search_users_curl_result = yield weibo_web_curl(Aim.search_users, keyword=keyword, user_type=user_type,
                                                        gender=gender, age_limit=age_limit, page_num=cursor)
        if not search_users_curl_result['error_code']:
            self.selector = search_users_curl_result['selector']
        else:
            error_res = curl_result_to_api_result(search_users_curl_result)
            self.write(error_res)
            return
        # 构建解析器
        searchUsersParser = SearchUsersParser(self.selector)
        # 提取信息
        user_list = searchUsersParser.parse_page()
        # 返回信息
        if user_list:
            success = const.SUCCESS.copy()
            success['data'] = {
                'result': user_list,
                'cursor': str(cursor + 1)
            }
            self.write(success)
            return
        self.write(WeiboCurlError.UNKNOWN_ERROR)
        return







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
        (ROUTE_PREFIX + r"statuses_user_timeline", UserTimelineHandler),
        (ROUTE_PREFIX + r"statuses_show", StatusesShowHandler),
        (ROUTE_PREFIX + r"friends_list", FriendsHandler),
        (ROUTE_PREFIX + r"followers_list", FollowersHandler),
        (ROUTE_PREFIX + r"search_tweets", SearchTweetsHandler),
        (ROUTE_PREFIX + r"users_search", SearchUsersHandler)
    ])

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()