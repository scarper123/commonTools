#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-06-14 10:22:21
# @Author  : Shanming Liu
# @Version : 1.0


class MyMetaclass(type):
    """docstring for MetaClass"""

    def __init__(cls, name, bases=None, attrs=None) -> None:
        print('MyMetaclass.__init__', cls, name, bases, attrs)
        super().__init__(name, bases, attrs)

    @staticmethod
    def __new__(mcs, name, bases=None, attrs=None):
        print('MyMetaclass.__new__', mcs, name, bases, attrs)
        return super().__new__(mcs, name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        """cls is the instance(class) of type"""
        print('MyMetaclass.__call__', cls, args, kwargs)
        return super().__call__(*args, **kwargs)


class MyClass(metaclass=MyMetaclass):
    """docstring for MyClass"""

    def __init__(self, *args, **kwargs) -> None:
        print('MyMetaclass.__init__', self, args, kwargs)
        super().__init__()

    @staticmethod
    def __new__(cls, *args, **kwargs):
        print('MyClass.__new__', cls, args, kwargs)
        return super().__new__(cls, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        """self is the instance of class"""
        print('MyClass.__call__', args, kwargs)

    def display(self):
        print('instance display')


class MyClass1(MyClass):
    """docstring for MyClass1"""

    @staticmethod
    def __new__(cls, *args, **kwargs):
        print('MyClass1.__new__', cls, args, kwargs)
        return super().__new__(cls, *args, **kwargs)


doc = """
1. __new__ is staticmethod, first parameter is class(type) self.
2. __call__ and __init__ is instance method, first parameter is instance of class(type)
"""

if __name__ == '__main__':
    c1 = MyClass()
    c2 = MyClass1()
    c1.display()
    c2.display()
    print(issubclass(type, object))
    print(type(type))
    print(type(object))
