# coding: utf-8
"""
    tests.test_core_wrappers_timeout
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend.core.wrappers.singleton test case

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""
import pytest

from pyextend.core.wrappers.timeout import timeout


def test_timeout():
    @timeout(2)
    def slowfunc(sleep_time):
        a = 1
        import time
        time.sleep(sleep_time)
        return a

    a = slowfunc(1)
    assert a == 1
    a = slowfunc(3)
    assert a == 1

if __name__ == '__main__':
    pytest.main(__file__)
