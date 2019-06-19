#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-06-14 10:22:21
# @Author  : Shanming Liu
# @Version : 1.0

from turtle import Turtle


class PigTurtle(Turtle):

    def nose(self, x, y):
        self.penup()
        self.goto(x, y)
        self.pendown()
        self.setheading(-30)

        self.begin_fill()
        a = 0.4

        for i in range(120):
            if 0 <= i < 30 or 60 <= i < 90:
                a = a + 0.08
                self.left(3)
                self.forward(a)
            else:
                a = a - 0.08
                self.left(3)
                self.forward(a)
                self.end_fill()

    def setting(self):
        self.pensize(4)
        self.hideturtle()
        self.screen.colormode(255)
        self.color((255, 155, 192), "pink")
        self.screen.setup(840, 500)
        self.speed(1)


def main():
    pig = PigTurtle()
    pig.setting()
    pig.nose(-100, 100)


if __name__ == '__main__':
    main()
