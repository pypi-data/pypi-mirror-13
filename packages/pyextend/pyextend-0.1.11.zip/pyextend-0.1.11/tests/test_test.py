import pytest
#
#
# def test_test():
#     assert 2 == 1+1
#
#
# def test_test2():
#     assert 1 == 1*1
#
#
# @pytest.mark.parametrize('_input, expected', [
#     ('3+5', 8),
#     ('1+5', 6),
#
# ])
# def test_eval(_input, expected):
#     assert eval(_input) == expected
#
#
# def test_zero_division():
#     with pytest.raises(ZeroDivisionError):
#         1/0
#
#
#
# def add(x, y):
#     return x+y
#
#
# @pytest.fixture(scope='module')
# def nums():
#     return [(x, 10*x) for x in range(10)]
#
#
# def test_fixture(nums):
#     output = []
#     for a, b in nums:
#         output.append(add(a, b))
#     expect = [0, 11, 22, 33, 44, 55, 66, 77, 88, 99]
#
#     assert output == expect
#
#
# def test_fixture2(nums):
#     assert nums == [(x, 10*x) for x in range(11)]
#

from pyextend.core.wrappers import sys


def test_system():
    @sys.platform(sys.WINDOWS)
    def _f():
        a = 1
        return a
    assert _f() == 1

if __name__ == '__main__':
    pytest.main(__file__)
