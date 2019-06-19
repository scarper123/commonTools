#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-06-14 10:22:21
# @Author  : Shanming Liu
# @Version : 1.0

import pprint


def functionTest():
    pass


class ClassTest(object):
    """docstring for ClassTest"""

    def __init__(self,):
        super(ClassTest, self).__init__()

    def selfMethodTest(self):
        pass

    @classmethod
    def classMethodTest(cls):
        pass

    @staticmethod
    def staticMethodTest():
        pass


if __name__ == '__main__':
    print(functionTest)
    print('*' * 100)
    print(ClassTest.selfMethodTest)
    print(ClassTest.classMethodTest)
    print(ClassTest.staticMethodTest)

    print('*' * 100)
    inst = ClassTest()
    print(inst.selfMethodTest)
    print(inst.classMethodTest)
    print(inst.staticMethodTest)

    print('*' * 100)
    pprint.pprint(dir(functionTest))
