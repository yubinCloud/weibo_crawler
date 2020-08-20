import sys
from const import LOGGING
from lxml import etree

def handle_garbled(info):
    """处理乱码"""
    try:
        _info = (info.xpath('string(.)').replace(u'\u200b', '').encode(
            sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding))
        return _info
    except Exception as e:
        LOGGING.exception(e)


def extract_from_one_table_node(table_node):
    """处理关注者或粉丝列表页中的一个table"""
    table_node = table_node.xpath('.//td')[1]
    follow_user = table_node.xpath('./a')[0]
    user_name = follow_user.text  # 关注者的昵称
    user_id = follow_user.get('href')  # 关注者的id
    if type(user_id) is str:
        user_id = user_id[user_id.rfind(r'/') + 1:]
    fans_num = table_node.xpath('text()')  # 关注者的粉丝数
    if len(fans_num) != 0:
        # fans_num = str(fans_num[0])
        fans_num = int(fans_num[0][2: -1])
    else:
        fans_num = None
    return dict(user_id=user_id, user_name=user_name, fans_num=fans_num)