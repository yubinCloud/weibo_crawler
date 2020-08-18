class WeiboCurlError:
    """各种微博爬取过程的错误类型"""

    # URL缺少参数
    URL_LACK_ARGS = {
        'error_code': 2001,
        'error_msg': 'URL is lack of arguments.'
    }

    # URL参数错误
    URL_ARGS_ERROR = {
        'error_code': 2002,
        'error_msg': 'URL args error.'
    }

    # 用户不存在
    USER_NOT_EXIST = {
        'error_code': 2004,
        'error_msg': "User don't exist."
    }

    # 微博网站返回其他错误信息
    OTHER_RESP_ERROR = {
        'error_code': 2005,
        'error_msg': "Sina weibo return a error http response."
    }

    # 未知错误
    UNKNOWN_ERROR = {
        'error_code': 2006,
        'error_msg': "An unknown error has occurred here."
    }


