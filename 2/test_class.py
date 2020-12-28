# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 13:45:55 2016

@author: ub71894 (4e8e6d0b), CSG
"""


class MyObject(object):
    def __init__(self,x,y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    def power(self):
        return self._x * self._y

aa= MyObject(4,9)

aa.power()
aa.y
aa.x

aa.x=10
aa.y=12

