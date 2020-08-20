import sys
from const import LOGGING


def handle_garbled(info):
    """处理乱码"""
    try:
        _info = (info.xpath('string(.)').replace(u'\u200b', '').encode(
            sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding))
        return _info
    except Exception as e:
        LOGGING.exception(e)