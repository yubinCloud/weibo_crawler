
# 发送一个request最多重新尝试的次数
RETRY_TIME = 3

# requests的headers
HEADERS = {
    "User-Agent": "MMozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36 Edg/84.0.522.52",
    "Cookie": """_T_WM=42850387063; SCF=Ag-pHF92PkAjbFi0TkzBe_0318uBL8w8f-n5-Db_tMuEuul6PBF1yvdrVsrZVZmmzoei55TgM95-MHMMXoVkoJY.; SUB=_2A25yL8vbDeRhGeBL7VsW9ybOwziIHXVR09WTrDV6PUJbktANLUTnkW1NRvHNwT7hyxWfVtDqzkf185J13WFW-qts; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFDZnCWr0kZqpYshkpRviAs5JpX5K-hUgL.FoqfSo.NS0nE1hB2dJLoI74KINLPqgpu9PzRSoBceBtt; SUHB=0Ry6363uEdCm-d; ALF=1599293579; MLOGIN=1; M_WEIBOCN_PARAMS=lfid%3D100103type%253D1%2526q%253D%25E6%2598%259F%25E7%2590%2583%25E5%25A4%25A7%25E6%2588%2598%26luicode%3D10000011"""
}

# requests的代理
PROXY = {
    "http": "http://36.249.119.57:9999"
}

# requests的超时时长限制das
REQUEST_TIME_OUT = 10

# 爬取结果正确时返回结果的格式
SUCCESS = {
    'error_code': 0,
    'data': None,
    'error_msg': ''
}

