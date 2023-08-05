# -*- coding: utf-8 -*-
__author__ = 'Administrator'
from ots2 import *



class Warriors:
    '''
       Warriors 分别有三个类：
       Warriors 为基础类
       Table    简单数据表添加和删除
       Row      简单行操作
       Engine   魔方引擎
    '''
    def __init__(self,EndPoint=None,AccessId=None,AccessSecret=None,InstanceName=None):
        self.EndPoint=EndPoint
        self.AccessId=AccessId
        self.AccessSecret=AccessSecret
        self.InstanceName=InstanceName





class WARRIORS_Error(Exception):
    def __init__(self,value):
        self.value=value

    def __str__(self):
        return repr(self.value)