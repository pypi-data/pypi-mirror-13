"""
A 64-bit universally unique identifier.
time (0-47)
node (48-63)
"""

from datetime import datetime
import os
import struct
import socket
import time

__author__ = 'Sumin Byeon'
__email__ = 'suminb@gmail.com'
__version__ = '0.1.0'


EPOCH = datetime(2015, 8, 1)


def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def uuid64_fields(uuid64):
    """
    :type uuid64: int
    """
    return (uuid64 >> 48, uuid64 & 0xFFFF)


class UUID64(object):
    def __init__(self, node_id):
        self.node_id = node_id

    def issue(self):
        time_seq = int(time.time() * 10000)

        return int(time_seq << 16 | self.node_id)


def issue():
    local_ip = os.environ.get(
        'IPV4_ADDR',
        socket.gethostbyname(socket.gethostname()))
    node_id = ip2int(local_ip) % (2 ** 16)
    uuid = UUID64(node_id)
    return uuid.issue()
