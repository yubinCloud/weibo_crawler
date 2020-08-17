class WeiboCrulError:
    """各种微博爬取过程的错误类型"""

    # cookie 无效
    COOKIR_INVALID = {
        'errpr_code': 2001,
        'error_msg': 'The weibo log cookie is invalid'
    }

