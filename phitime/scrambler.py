from pyramid.threadlocal import get_current_registry

import logging
import six

log = logging.getLogger(__name__)

def scramble(i):
    """scramble int id to hex string
    :param i: unscramble id
    :type i: int
    :return: scrambled id
    :rtype: str
    """
    salt = int(get_current_registry().settings['phitime.scramble_salt'])
    inverse_salt = int(get_current_registry().settings['phitime.scramble_inverse_salt'])

    def _reverse(n):
        n = ((n >> 1) & 0x55555555) | ((n & 0x55555555) << 1)
        n = ((n >> 2) & 0x33333333) | ((n & 0x33333333) << 2)
        n = ((n >> 4) & 0x0F0F0F0F) | ((n & 0x0F0F0F0F) << 4)
        n = ((n >> 8) & 0x00FF00FF) | ((n & 0x00FF00FF) << 8)
        n = (n >> 16) | (n << 16)
        return n

    def _trim(n):
        return n & 0xffffffff

    res = _trim(_reverse(_trim(i * salt)) * inverse_salt)
    res = hex(res)[2:].replace('L', '')
    res = res.rjust(8, '0')
    return res


def unscramble(s):
    """unscramble hex string to int id
    :param s: 
    :return:
    """
    if isinstance(s, six.string_types):
        i = int(s, 16)
        return int(scramble(i), 16)
    raise ValueError('unscramble require hex string')