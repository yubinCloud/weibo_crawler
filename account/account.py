from const import LOGGING
import json

class Account:
    """一个账号，包含cookie和proxy"""
    def __init__(self, cookie, proxy):
        self.cookie = cookie
        self.proxy = proxy  # proxy[0]为proxy_host， proxy[1]为proxy_port

    def __repr__(self):
        return "proxy: {}, cookie: {}".format(self.proxy, self.cookie)


class AccountPool:
    """账号池，管理cookie和ip"""
    def __init__(self, cookies, proxies):
        if not cookies or not proxies:
            raise ValueError
        if type(cookies) is not list or type(proxies) is not list:
            raise TypeError

        self.cookies = cookies
        self.proxies = proxies
        self.accounts = list()
        self.count = 0
        self._compound_accounts()

    def __repr__(self):
        return '\n'.join(self.accounts)

    def _compound_accounts(self):
        """根据cookies和proxies合成所有Account对象"""
        cookies_len = len(self.cookies)
        proxies_len = len(self.proxies)
        max_len = max(cookies_len, proxies_len)

        self.accounts.clear()
        for i in range(max_len):
            account = Account(self.cookies[i % cookies_len], self.proxies[i % proxies_len])
            self.accounts.append(account)

    def update(self, new_cookies=None, new_proxies=None):
        """对信息进行更新"""
        if new_cookies is not None and len(new_cookies) == 0:
            raise ValueError
        if new_proxies is not None and len(new_proxies) == 0:
            raise ValueError

        if new_cookies:
            self.cookies = new_cookies
        if new_proxies:
            self.accounts = new_proxies
        self._compound_accounts()

    def update_one_cookie(self, seq_num, new_cookie):
        try:
            self.accounts[seq_num].cookie = new_cookie
        except IndexError:
            LOGGING.warning("update fail because seq_num {} over the max account number {}."
                            .format(seq_num, len(self.accounts)))

    def update_one_proxy(self, seq_num, new_proxy):
        try:
            self.accounts[seq_num].proxy = new_proxy
        except IndexError:
            LOGGING.warning("update fail because seq_num {} over the max account number {}."
                            .format(seq_num, len(self.accounts)))

    def delete_one_proxy(self, seq_num):
        try:
            del self.accounts[seq_num]
        except IndexError:
            LOGGING.warning("delete fail because seq_num {} over the max account number {}."
                            .format(seq_num, len(self.accounts)))

    def fetch(self):
        """获取一个账号的cookie和代理"""
        self.count += 1
        self.count = self.count % len(self.accounts)
        account = self.accounts[self.count]
        return account.cookie, account.proxy


with open(r'X:\Python\workbook\weibo_curl\account\account.json') as json_file:
    account_json = json.load(json_file)

account_pool = AccountPool(account_json['cookies'], account_json['proxies'])