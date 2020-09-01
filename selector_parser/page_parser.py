import random
from datetime import datetime, timedelta
import re
import sys
from time import sleep
from lxml import etree

from tornado import gen
import requests

import utils
from settings import LOGGING
from web_curl import Aim, weibo_web_curl
import settings
from .base_parser import BaseParser
from weibo_curl_error import HTMLParseException


class PageParser(BaseParser):
    def __init__(self, user_id, response, filter):
        super().__init__(response)
        self.user_id = user_id
        self.filter = filter  # 值为1代表爬取全部原创微博，0代表爬取全部微博（原创+转发）

    @gen.coroutine
    def get_one_page(self):
        """获取第page页的全部微博"""
        weibo_id_list = list()  # 存储微博的id
        weibos = list()         # 存储所有微博的信息
        try:
            all_weibo_info = self.selector.xpath("//div[@class='c']")
            is_exist = all_weibo_info[0].xpath("div/span[@class='ctt']")
            if is_exist:
                for i in range(0, len(all_weibo_info) - 2):
                    weibo = yield self.get_one_weibo(all_weibo_info[i])
                    if weibo:
                        if weibo.weibo_id in weibo_id_list:
                            continue
                        LOGGING.info(weibo)
                        LOGGING.info('-' * 100)
                        weibos.append(weibo)
                        weibo_id_list.append(weibo.weibo_id)
            return weibos, weibo_id_list
        except Exception as e:
            LOGGING.warning('{} occur a error: {}'.format(
                '.'.join((__class__.__name__, sys._getframe().f_code.co_name)), e))
            raise HTMLParseException

    def is_original(self, info):
        """判断微博是否为原创微博"""
        is_original = info.xpath("div/span[@class='cmt']")
        if len(is_original) > 3:
            return False
        else:
            return True

    @gen.coroutine
    def get_original_weibo(self, info, weibo_id):
        """获取原创微博"""
        try:
            weibo_content = utils.handle_garbled(info)
            weibo_content = weibo_content[:weibo_content.rfind(u'赞')]
            a_text = info.xpath('div//a/text()')
            if u'全文' in a_text:
                wb_content = yield CommentParser(weibo_id).get_long_weibo()
                if wb_content:
                    weibo_content = wb_content
            return dict(weibo_content=weibo_content)
        except Exception as e:
            LOGGING.warning('{} occur a error: {}'.format(
                '.'.join((__class__.__name__, sys._getframe().f_code.co_name)), e))
            raise HTMLParseException

    @gen.coroutine
    def get_retweet(self, info, weibo_id):
        """获取转发微博"""
        try:
            weibo_content = utils.handle_garbled(info)
            weibo_content = weibo_content[weibo_content.find(':') +
                                          1:weibo_content.rfind(u'赞')]
            weibo_content = weibo_content[:weibo_content.rfind(u'赞')]
            # 检查当前是否已经为全部微博内容
            a_text = info.xpath('div//a/text()')
            if u'全文' in a_text:
                wb_content = yield CommentParser(weibo_id).get_long_retweet()
                if wb_content:
                    weibo_content = wb_content
            # 提取转发理由
            retweet_reason = utils.handle_garbled(info.xpath('div')[-1])
            retweet_reason = retweet_reason[:retweet_reason.rindex(u'赞')]
            # 提取原始用户
            original_user = info.xpath("div/span[@class='cmt']/a/text()")

            content_info = None  # 微博内容信息
            if original_user:
                original_user = original_user[0]
                content_info = {
                    'retweet_reason': retweet_reason,   # 转发理由
                    'original_user': original_user,     # 原始用户名
                    'weibo_content': weibo_content      # 转发内容
                }
            else:
                content_info = {
                    'retweet_reason': retweet_reason,  # 转发理由
                    'original_user': None,  # 原始用户名
                    'weibo_content': weibo_content  # 转发内容
                }
            return content_info
        except Exception as e:
            LOGGING.warning('{} occur a error: {}'.format(
                '.'.join((__class__.__name__, sys._getframe().f_code.co_name)), e))
            raise HTMLParseException

    @gen.coroutine
    def get_weibo_content(self, info, is_original):
        """获取微博内容"""
        try:
            weibo_id = info.xpath('@id')[0][2:]
            if is_original:
                weibo_content_info = yield self.get_original_weibo(info, weibo_id)
            else:
                weibo_content_info = yield self.get_retweet(info, weibo_id)
            return weibo_content_info
        except Exception as e:
            LOGGING.warning('{} occur a error: {}'.format(
                '.'.join((__class__.__name__, sys._getframe().f_code.co_name)), e))
            raise HTMLParseException

    def get_article_url(self, info):
        """获取微博头条文章的url"""
        article_url = ''
        text = utils.handle_garbled(info)
        if text.startswith(u'发布了头条文章'):
            url = info.xpath('.//a/@href')
            if url and url[0].startswith('https://weibo.cn/sinaurl'):
                article_url = url[0]
        return article_url

    def get_publish_place(self, info):
        """获取微博发布位置"""
        try:
            div_first = info.xpath('div')[0]
            a_list = div_first.xpath('a')
            publish_place = u'无'
            for a in a_list:
                if ('place.weibo.com' in a.xpath('@href')[0]
                        and a.xpath('text()')[0] == u'显示地图'):
                    weibo_a = div_first.xpath("span[@class='ctt']/a")
                    if len(weibo_a) >= 1:
                        publish_place = weibo_a[-1]
                        if (u'视频' == div_first.xpath(
                                "span[@class='ctt']/a/text()")[-1][-2:]):
                            if len(weibo_a) >= 2:
                                publish_place = weibo_a[-2]
                            else:
                                publish_place = u'无'
                        publish_place = utils.handle_garbled(publish_place)
                        break
            return publish_place
        except Exception as e:
            LOGGING.warning('{} occur a error: {}'.format(
                '.'.join((__class__.__name__, sys._getframe().f_code.co_name)), e))
            raise HTMLParseException

    def get_publish_time(self, info):
        """获取微博发布时间"""
        try:
            str_time = info.xpath("div/span[@class='ct']")
            str_time = utils.handle_garbled(str_time[0])
            publish_time = str_time.split(u'来自')[0]
            if u'刚刚' in publish_time:
                publish_time = datetime.now().strftime('%Y-%m-%d %H:%M')
            elif u'分钟' in publish_time:
                minute = publish_time[:publish_time.find(u'分钟')]
                minute = timedelta(minutes=int(minute))
                publish_time = (datetime.now() -
                                minute).strftime('%Y-%m-%d %H:%M')
            elif u'今天' in publish_time:
                today = datetime.now().strftime('%Y-%m-%d')
                time = publish_time[3:]
                publish_time = today + ' ' + time
                if len(publish_time) > 16:
                    publish_time = publish_time[:16]
            elif u'月' in publish_time:
                year = datetime.now().strftime('%Y')
                month = publish_time[0:2]
                day = publish_time[3:5]
                time = publish_time[7:12]
                publish_time = year + '-' + month + '-' + day + ' ' + time
            else:
                publish_time = publish_time[:16]
            return publish_time
        except Exception as e:
            LOGGING.warning('{} occur a error: {}'.format(
                '.'.join((__class__.__name__, sys._getframe().f_code.co_name)), e))
            raise HTMLParseException

    def get_publish_tool(self, info):
        """获取微博发布工具"""
        try:
            str_time = info.xpath("div/span[@class='ct']")
            str_time = utils.handle_garbled(str_time[0])
            if len(str_time.split(u'来自')) > 1:
                publish_tool = str_time.split(u'来自')[1]
            else:
                publish_tool = u'无'
            return publish_tool
        except Exception as e:
            LOGGING.warning('{} occur a error: {}'.format(
                '.'.join((__class__.__name__, sys._getframe().f_code.co_name)), e))
            raise HTMLParseException

    def get_weibo_footer(self, info):
        """获取微博点赞数、转发数、评论数"""
        try:
            footer = {}
            pattern = r'\d+'
            str_footer = info.xpath('div')[-1]
            str_footer = utils.handle_garbled(str_footer)
            str_footer = str_footer[str_footer.rfind(u'赞'):]
            weibo_footer = re.findall(pattern, str_footer, re.M)

            up_num = int(weibo_footer[0])
            footer['up_num'] = up_num

            retweet_num = int(weibo_footer[1])
            footer['retweet_num'] = retweet_num

            comment_num = int(weibo_footer[2])
            footer['comment_num'] = comment_num
            return footer
        except Exception as e:
            LOGGING.warning('{} occur a error: {}'.format(
                '.'.join((__class__.__name__, sys._getframe().f_code.co_name)), e))
            raise HTMLParseException

    @gen.coroutine
    def get_picture_urls(self, info, is_original):
        """获取微博原始图片url"""
        try:
            weibo_id = info.xpath('@id')[0][2:]
            picture_urls = {}
            if is_original:
                original_pictures = yield self.extract_picture_urls(info, weibo_id)
                picture_urls['original_pictures'] = original_pictures
                if not self.filter:
                    picture_urls['retweet_pictures'] = list()
            else:
                retweet_url = info.xpath("div/a[@class='cc']/@href")[0]
                retweet_id = retweet_url.split('/')[-1].split('?')[0]
                retweet_pictures = yield self.extract_picture_urls(info, retweet_id)
                picture_urls['retweet_pictures'] = retweet_pictures
                a_list = info.xpath('div[last()]/a/@href')
                original_picture = u'无'
                for a in a_list:
                    if a.endswith(('.gif', '.jpeg', '.jpg', '.png')):
                        original_picture = a
                        break
                picture_urls['original_pictures'] = original_picture
            return picture_urls
        except Exception as e:
            LOGGING.warning('{} occur a error: {}'.format(
                '.'.join((__class__.__name__, sys._getframe().f_code.co_name)), e))
            raise HTMLParseException

    def get_video_url(self, info, is_original):
        """获取微博视频url"""
        try:
            video_url = u'无'
            if is_original:
                div_first = info.xpath('div')[0]
                a_list = div_first.xpath('.//a')
                video_link = u'无'
                for a in a_list:
                    if 'm.weibo.cn/s/video/show?object_id=' in a.xpath(
                            '@href')[0]:
                        video_link = a.xpath('@href')[0]
                        break
                if video_link != u'无':
                    video_link = video_link.replace(
                        'm.weibo.cn/s/video/show', 'm.weibo.cn/s/video/object')
                    wb_info = requests.get(video_link, headers=settings.get_headers()).json()
                    video_url = wb_info['data']['object']['stream'].get(
                        'hd_url')
                    if not video_url:
                        video_url = wb_info['data']['object']['stream']['url']
                        if not video_url:  # 说明该视频为直播
                            video_url = u'无'
            return video_url
        except Exception as e:
            LOGGING.warning('{} occur a error: {}'.format(
                '.'.join((__class__.__name__, sys._getframe().f_code.co_name)), e))
            return u'无'

    def is_pinned_weibo(self, info):
        """判断微博是否为置顶微博"""
        kt = info.xpath(".//span[@class='kt']/text()")
        if kt and kt[0] == u'置顶':
            return True
        else:
            return False

    @gen.coroutine
    def get_one_weibo(self, info):
        """获取一条微博的全部信息"""
        try:
            weibo = Weibo()
            weibo.user_id = self.user_id
            is_original = self.is_original(info)
            if (not self.filter) or is_original:
                weibo.weibo_id = info.xpath('@id')[0][2:]
                weibo.content = yield self.get_weibo_content(info,
                                                       is_original)  # 微博内容
                weibo.article_url = self.get_article_url(info)  # 头条文章url
                picture_urls = yield self.get_picture_urls(info, is_original)
                weibo.original_pictures = picture_urls[
                    'original_pictures']  # 原创图片url
                if not self.filter:
                    weibo.retweet_pictures = picture_urls[
                        'retweet_pictures']  # 转发图片url
                    weibo.original = is_original  # 是否原创微博
                weibo.video_url = self.get_video_url(info,
                                                     is_original)  # 微博视频url
                weibo.publish_place = self.get_publish_place(info)  # 微博发布位置
                weibo.publish_time = self.get_publish_time(info)  # 微博发布时间
                weibo.publish_tool = self.get_publish_tool(info)  # 微博发布工具
                footer = self.get_weibo_footer(info)
                weibo.up_num = footer['up_num']  # 微博点赞数
                weibo.retweet_num = footer['retweet_num']  # 转发数
                weibo.comment_num = footer['comment_num']  # 评论数
            else:
                weibo = None
                LOGGING.info(u'正在过滤转发微博')
            return weibo
        except Exception as e:
            LOGGING.warning('{} occur a error: {}'.format(
                '.'.join((__class__.__name__, sys._getframe().f_code.co_name)), e))
            raise HTMLParseException

    @gen.coroutine
    def extract_picture_urls(self, info, weibo_id):
        """提取微博原始图片url"""
        try:
            a_list = info.xpath('div/a/@href')
            first_pic = 'https://weibo.cn/mblog/pic/' + weibo_id
            all_pic = 'https://weibo.cn/mblog/picAll/' + weibo_id
            picture_urls = list()
            if first_pic in ''.join(a_list):
                if all_pic in ''.join(a_list):
                    mblog_picall_curl_result = yield weibo_web_curl(Aim.mblog_pic_all, weibo_id=weibo_id)
                    mblogPicAllParser = None
                    if not mblog_picall_curl_result['error_code']:
                        mblogPicAllParser = MblogPicAllParser(mblog_picall_curl_result['selector'])
                    preview_picture_list = mblogPicAllParser.extract_preview_picture_list()
                    picture_urls = [
                        p.replace('/thumb180/', '/large/')
                        for p in preview_picture_list
                    ]
                else:
                    if info.xpath('.//img/@src'):
                        for link in info.xpath('div/a'):
                            if len(link.xpath('@href')) > 0:
                                if first_pic in link.xpath('@href')[0]:
                                    if len(link.xpath('img/@src')) > 0:
                                        preview_picture = link.xpath(
                                            'img/@src')[0]
                                        picture_urls = [preview_picture.replace('/wap180/', '/large/')]
                                        break
                    else:
                        LOGGING.warning(
                            u'爬虫微博可能被设置成了"不显示图片"，请前往'
                            u'"https://weibo.cn/account/customize/pic"，修改为"显示"'
                        )
                        sys.exit()
            return picture_urls
        except Exception as e:
            LOGGING.warning('{} occur a error: {}'.format(
                '.'.join((__class__.__name__, sys._getframe().f_code.co_name)), e))
            return u'无'


class MblogPicAllParser(BaseParser):
    def __init__(self, response):
        super().__init__(response)

    def extract_preview_picture_list(self):
        return self.selector.xpath('//img/@src')


class Weibo:
    """一条微博的信息"""
    def __init__(self):
        self.weibo_id = ''
        self.user_id = ''

        self.content = ''
        self.article_url = ''

        self.original_pictures = []
        self.retweet_pictures = None
        self.original = None
        self.video_url = ''

        self.publish_place = ''
        self.publish_time = ''
        self.publish_tool = ''

        self.up_num = 0
        self.retweet_num = 0
        self.comment_num = 0

    def __str__(self):
        """打印一条微博"""
        result = self.content + '\n'
        result += u'微博发布位置：%s\n' % self.publish_place
        result += u'发布时间：%s\n' % self.publish_time
        result += u'发布工具：%s\n' % self.publish_tool
        result += u'点赞数：%d\n' % self.up_num
        result += u'转发数：%d\n' % self.retweet_num
        result += u'评论数：%d\n' % self.comment_num
        result += u'url：https://weibo.cn/comment/%s\n' % self.weibo_id
        return result


class CommentParser(BaseParser):
    def __init__(self, weibo_id, response=None):
        super().__init__(response)
        self.weibo_id = weibo_id

    @gen.coroutine
    def get_long_weibo(self):
        """获取长原创微博"""

        try:
            for i in range(5):
                if self.selector is None or i != 0:  # 当selector为空时进行爬取网页
                    comment_curl_result = yield weibo_web_curl(Aim.weibo_comment, weibo_id=self.weibo_id)
                    if not comment_curl_result['error_code']:
                        self.selector = etree.HTML(comment_curl_result['response'].body)
                    else:
                        self.selector = None

                if self.selector is not None:
                    info = self.selector.xpath("//div[@id='M_']")[0]
                    wb_content = utils.handle_garbled(info)
                    wb_time = info.xpath("//span[@class='ct']/text()")[0]
                    weibo_content = wb_content[wb_content.find(':') +
                                               1:wb_content.rfind(wb_time)]
                    if weibo_content is not None:
                        return weibo_content
                sleep(random.randint(6, 10))
        except Exception as e:
            LOGGING.warning('{} occur a error: {}'.format(
                '.'.join((__class__.__name__, sys._getframe().f_code.co_name)), e))
            raise HTMLParseException

    @gen.coroutine
    def get_long_retweet(self, rev_type=str):
        """获取长转发微博"""
        try:
            wb_content = yield self.get_long_weibo()
            retweet_content = wb_content[:wb_content.find(u'原文转发')]  # 转发内容的原文
            retweet_reason = wb_content[wb_content.find(u'转发理由:') + 5: ]  # 转发理由

            if rev_type is dict:
                return {
                    'retweet': retweet_content,
                    'retweet_reason': retweet_reason
                }
            return '转发原文：{}\n转发理由：{}'.format(retweet_content, retweet_reason)

        except Exception as e:
            LOGGING.warning('{} occur a error: {}'.format(
                '.'.join((__class__.__name__, sys._getframe().f_code.co_name)), e))
            raise HTMLParseException

    def get_footer(self):
        """获取转发量、评论数、赞"""
        span_nodes = self.selector.xpath(r'/html/body/div/span')
        # 转发量
        text = span_nodes[0].xpath(r'/a/text()')[0]
        retweet_num = text[text.find('['): text.rfind(']')]
        retweet_num = int(retweet_num)
        # 评论数
        text = span_nodes[1].xpath(r'/text()')[0]
        comment_num = text[text.find('['): text.find(']')]
        comment_num = int(comment_num)
        # 赞
        text = span_nodes[2].xpath(r'/a/text()')[0]
        up_num = text[text.find('['): text.find(']')]
        up_num = int(up_num)

        return {
            'retweet_num': retweet_num,
            'comment_num': comment_num,
            'up_num': up_num
        }

    def is_original(self):
        """检查是否为原创"""
        if self.selector is None:
            return True
        else:
            res = self.selector.xpath('//*[@id="M_"]/div/span[@class="cmt"]')
            return True if len(res) == 0 else False


    def get_user(self):
        """获取用户的id和用户名"""
        user_node = self.selector.xpath('//*[@id="M_"]/div[1]/a')[0]
        user_id = user_node.get('href')
        user_id = user_id[user_id.rfind(r'/') + 1: ]
        user_name = user_node.text
        return user_id, user_name

    def get_all_comment(self):
        """获取评论"""
        comment_list = list()
        all_div = self.selector.xpath('/html/body/div[@class="c"]')
        for div in all_div:
            id_value = div.get('id')
            if id_value is not None and id_value.find('C_') != -1:
                try:
                    comment = CommentParser._parse_one_comment(div)
                except Exception as e:
                    LOGGING.warning(e)
                    print(e)
                    comment = None
                if comment is not None:
                    comment_list.append(comment)
        return comment_list

    COMMENT_TEMPLATE = {
        'is_hot': False,  # 是否为热评
        'user_id': None,  # 评论用户的id
        'screen_name': None,  # 评论用户的用户名
        'content': None,  # 评论内容
        'like_num': None,  # 点赞数
        'publish_info': None  # 发布信息（包括时间和发布工具）
    }

    @staticmethod
    def _parse_one_comment(node):
        comment = CommentParser.COMMENT_TEMPLATE.copy()
        span_nodes = node.xpath('./span')
        for span_node in span_nodes:
            klass = span_node.get('class')
            if klass == 'kt':
                comment['is_hot'] = True
            elif klass == 'ctt':
                comment['content'] = ''.join(span_node.xpath('./text()'))
            elif klass == 'cc':
                text = ''.join(span_node.xpath('./a/text()'))
                pos = text.find('赞')
                if pos != -1:
                    comment['like_num'] = text[pos + 2: -1]
            elif klass == 'ct':
                comment['publish'] = ''.join(span_node.xpath('./text()'))

        user_node = node.xpath('./a')[0]
        comment['screen_name'] = user_node.xpath('./text()')[0]
        user_href = user_node.get('href')
        comment['user_id'] = user_href[user_href.rfind(r'/') + 1: ]
        return comment


