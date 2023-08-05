#!/usr/bin/env python
# coding=utf-8
#从python发布工具包导入“setup”函数
from distutils.core import setup
#将模块的元数据与setup函数的参数关联
setup(
    name = 'Demo1',
    version = '1.0.0',
    py_modules = ['Demo1'],
    author = 'peerslee',
    )
