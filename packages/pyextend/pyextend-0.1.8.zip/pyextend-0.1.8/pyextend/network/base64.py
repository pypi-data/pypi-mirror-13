# coding: utf-8
"""
    pyextend.network.base64
    ~~~~~~~~~~~~~~~~~~~~~
    pyextend network base64

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""

import base64


def safe_base64_decode(s):
    s += (-len(s) % 4)*b'='
    print(s)
    return base64.b64decode(s)

if __name__ == '__main__':
    assert b'abcd' == safe_base64_decode(b'YWJjZA=='), safe_base64_decode('YWJjZA==')
    assert b'abcd' == safe_base64_decode(b'YWJjZA'), safe_base64_decode('YWJjZA')
    assert b'abcde' == safe_base64_decode(b'YWJjZGU'), safe_base64_decode(b'YWJjZGU')
    print('Pass')
