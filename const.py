import logging
import requests
from queue import Queue

PORT_NUM = 8000  # app运行的端口号


def get_account():
    """
    获取一对账号与密码
    :return: (username, password)
    """
    return ('xxxxx', 'xxxxx')


# 发送一个request最多重新尝试的次数
RETRY_TIME = 3

# requests的headers
HEADERS = {
    "User-Agent": "MMozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36 Edg/84.0.522.52",
}
HEADERS_WITH_COOKIR = HEADERS.copy()
HEADERS_WITH_COOKIR["Cookie"] = """_T_WM=61471365121; MLOGIN=0; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5ObAfXIyBuBI7M63Sw-Yi65NHD95QNShnc1Ke7e0-7Ws4DqcjMi--NiK.Xi-2Ri--ciKnRi-zNS0BRSo.0ehefe5tt; SCF=Ag-pHF92PkAjbFi0TkzBe_0318uBL8w8f-n5-Db_tMuEhKx8WKiMJmwit3GoFxbbfVW8V8aXfHeYyhneZI662lc.; SUB=_2A25yO2V0DeRhGeFK41QY8y7PzjyIHXVRxAs8rDV6PUJbktAKLVLNkW1NQsPSalyQszk2bQN3XQ0KqA83OXSbykeK; SUHB=02Mvtd78rPWdTG; SSOLoginState=1597969700"""


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


# requests的代理池
proxy_pool = Queue(maxsize=-1)

def init_proxy_pool(proxy_pool):
    proxy_pool.put({'host': '60.179.200.156', 'port': 3000})

init_proxy_pool(proxy_pool)

def get_proxy():
    """
    获取代理
    """
    cur_proxy = proxy_pool.get()
    proxy_pool.put(cur_proxy)
    return cur_proxy['host'], cur_proxy['port']


# requests的超时时长限制das
REQUEST_TIME_OUT = 10

# 爬取结果正确时返回结果的格式
SUCCESS = {
    'error_code': 0,
    'data': None,
    'error_msg': None
}

# 日志
LOGGING = logging

if __name__ == "__main__":
    update_cookie()
    print(HEADERS_WITH_COOKIR["Cookie"])