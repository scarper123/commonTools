#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-06-14 10:22:21
# @Author  : Shanming Liu
# @Version : 1.0

import functools


class MyStaticMethod(object):
    """docstring for MyStaticMethod"""

    def __init__(self, fget=None, fset=None, fdel=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel

    def __get__(self, obj, cls=None):
        return self.fget


class MyClassMethod(object):
    """docstring for MyClassMethod"""

    def __init__(self, fget=None, fset=None, fdel=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel

    def __get__(self, obj, cls):
        return functools.partial(self.fget, cls)


class ClassTest(object):
    """docstring for ClassTest"""
    @MyStaticMethod
    def staticTest(*args, **kwargs):
        print(args, kwargs)

    @MyClassMethod
    def classTest(cls, *args, **kwargs):
        print(cls, args, kwargs)
        return cls()


if __name__ == '__main__':
    ClassTest.staticTest('aaa')
    test = ClassTest()
    test.staticTest('aaa')
    instance = test.classTest('aaa')
    instance.classTest('bbb')
    ClassTest.classTest('ccc')
