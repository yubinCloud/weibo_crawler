import logging
import requests

def get_account():
    """
    获取一对账号与密码
    :return: (username, password)
    """
    return ('17863116898', 'yubin3869')


# 发送一个request最多重新尝试的次数
RETRY_TIME = 3

# requests的headers
HEADERS = {
    "User-Agent": "MMozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36 Edg/84.0.522.52",
}
HEADERS_WITH_COOKIR = HEADERS.copy()
HEADERS_WITH_COOKIR["Cookie"] = """SCF=Au_FGdKVc5NVf8bEdaC7IYLsLT1cCDiDxnY2ufmdfGIqiLNdi0VtQcWUNAZpwX6qas9_grOBVQd7PbXJPxacREw.; SSOLoginState=1597717597; SUB=_2A25yP0wNDeRhGeFK41QY8y7PzjyIHXVRwFRFrDV6PUJbkdANLVHFkW1NQsPSaqBq_yp3Oo3rcKAJpsXblqNTRkKh; SUHB=0ebtiEkMtM4DcG"""


def get_headers(with_cookie=True):
    """
    获取一个Request的Headers
    """
    return HEADERS_WITH_COOKIR if with_cookie else HEADERS


def update_cookie():
    """
    通过模拟登陆对cookie进行更新
    """
    url = r'https://passport.weibo.cn/sso/login'
    username, password = get_account()
    # 构造参数字典
    data = {'username': username,
            'password': password,
            'savestate': '1',
            'r': r'',
            'ec': '0',
            'pagerefer': '',
            'entry': 'mweibo',
            'wentry': '',
            'loginfrom': '',
            'client_id': '',
            'code': '',
            'qq': '',
            'mainpageflag': '1',
            'hff': '',
            'hfp': ''}
    # headers，防屏
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
        'Accept': 'text/html;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Connection': 'close',
        'Referer': 'https://passport.weibo.cn/signin/login',
        'Host': 'passport.weibo.cn'
    }
    # 模拟登录
    session = requests.session()
    session.post(url=url, data=data, headers=headers)
    # 获取 Cookie 并更新到 HEADERS_WITH_COOKIR
    resp = session.get('https://weibo.cn')
    HEADERS_WITH_COOKIR["Cookie"] = resp.headers.get('Cookie')


# requests的代理
PROXY = {
    "http": "http://36.249.119.57:9999"
}

def get_proxy():
    """
    获取代理
    """
    return PROXY


# requests的超时时长限制das
REQUEST_TIME_OUT = 10

# 爬取结果正确时返回结果的格式
SUCCESS = {
    'error_code': 0,
    'data': None,
    'error_msg': ''
}

# 日志
LOGGING = logging