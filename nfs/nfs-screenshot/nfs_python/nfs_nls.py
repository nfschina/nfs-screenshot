#!/usr/bin/python
#-*- coding:utf-8 -*-
#Copyright (c) 2016-2018 CPU and Fundamental Software Research Center, CAS
#Based on code from src/main.py in deepin-screenshot-2.0
# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hou Shaohui
# 
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou Shaohui <houshao55@gmail.com>
#This software is published by the license of CPU-OS License，you can use and 
#distibuted this software under this License. See CPU-OS Liense for more detail.
#You should have receive a copy of CPU-OS License. If not, please contact us 
#by email <support_os@cpu-os.ac.cn> 
#模块描述：
#
#
#作者: liangjian
#日期：2014-08-20

import gettext
import os
import locale

default_locale = locale.getdefaultlocale()[0]

def get_parent_dir(filepath, level=1):
    '''Get parent dir.'''
    parent_dir = os.path.realpath(filepath)

    while(level > 0):
        parent_dir = os.path.dirname(parent_dir)
        level -= 1

    return parent_dir

LOCALE_DIR=os.path.join(get_parent_dir(__file__, 2), "locale")
if not os.path.exists(LOCALE_DIR):
    LOCALE_DIR="/usr/share/locale"

_ = None
try:
    _ = gettext.translation("screenshot", LOCALE_DIR).gettext
except Exception, e:
    _ = lambda i : i
