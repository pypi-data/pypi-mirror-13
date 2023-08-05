# -*- coding: utf-8 -*-

"""
List-related parsing.
"""

import re
from mekk.fics.datatypes.channel import ChannelRef

re_plus_channel = re.compile('^\[(?P<no>\d+)\] added to your channel list')

def parse_addlist_reply(reply_text):
    """
    Parse reply to +chan, +notify etc.
    :param reply_text: FICS reply
    :type reply_text: str
    """
    m = re_plus_channel.search(reply_text)
    if m:
        return ChannelRef(int(m.group('no')))
    return None
