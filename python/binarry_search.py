#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-06-14 10:22:21
# @Author  : Shanming Liu
# @Version : 1.0

import random


def binarrySearch(array, value):
    if not array:
        return

    inx = len(array) // 2
    if array[inx] == value:
        return array[inx]
    elif array[inx] < value:
        return binarrySearch(array[inx + 1:], value)
    else:
        return binarrySearch(array[:inx], value)


def lineSearch(array, value):
    for item in array:
        if value == item:
            return item


def main():
    array = list(range(100000000))
    value = random.randint(0, len(array))

    print(value)
    assert lineSearch(array, value) == value


if __name__ == '__main__':
    main()
