#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-06-14 10:22:21
# @Author  : Shanming Liu
# @Version : 1.0


import os


class MyProperty(object):
    """docstring for MyProperty"""

    def __init__(self, fget=None, fset=None, fdel=None):
        print('init property')
        super(MyProperty, self).__init__()
        self.fget = fget
        self.fset = fset
        self.fdel = fdel

    def __get__(self, obj, cls):
        print('MyProperty get')
        print(obj)
        print(cls)
        return self.fget(obj)

    def __set__(self, obj, value):
        print('MyProperty set')
        self.fset(obj, value)

    def __delete__(self, obj):
        print('MyProperty del')
        self.fdel(obj)

    def __call__(self):
        print('MyProperty call')
        return 1000

    def setter(self, fset):
        print('setter property')
        self.fset = fset
        return self

    def deleter(self, fdel):
        print('deleter property')
        self.fdel = fdel
        return self


class C(object):
    """docstring for C"""

    def __init__(self):
        super(C, self).__init__()
        self._value = 10

    @MyProperty
    def value(self):
        return self._value

    # @property
    # def value1(self):
    #     return self._value

    # def value2(self):
    #     return self._value

    @value.setter
    def value1(self, value):
        self._value = value

    @value.deleter
    def value2(self):
        print('C value delete')
        del self._value

    def __getattribute__(self, name):
        print('C __getattribute__ %s' % name)
        return super().__getattribute__(name)

    def __getattr__(self, name):
        print('C __getattr__ %s' % name)
        raise AttributeError(name)


doc = """
attribute get steps:
    1. instance.__getattribute__,
        this will find in the instance.__dict__ or class.__dict__
    2. Check the class.__dict__[name] has the __get__ method,
        if has use __get__(instance, cls)
    3. instance.__getattr__,
        not found any return value on up steps

classmethod and staticmethod are also property use
"""


def main():
    print(C.__dict__)
    c = C()
    # print(c.__dict__)
    print(c.value)
    # print(c.test)
    c.value = 10000

    print(c.value)
    # print(c.__dict__)
    # del c.value
    # print(c.__dict__)


if __name__ == '__main__':
    main()
