#!/usr/bin/python
#-*- coding:utf-8 -*-
#Copyright (c) 2016-2018 CPU and Fundamental Software Research Center, CAS
#Based on code from src/constant.py in deepin-screenshot-2.0
#Copyright (C) 2011 Deepin, Inc.
#               2011 Wang Yong
#
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>

#模块描述：
#   常量类
#
#作者: liangjian
#日期：2014-08-20
#This software is published by the license of CPU-OS License，you can use and 
#distibuted this software under this License.See CPU-OS Liense for more detail.
#You should have receive a copy of CPU-OS License.If not,please contact us 
#by email <support_os@cpu-os.ac.cn> 
'''
显示状态
@var ACTION_WINDOW_INIT: 开始选择区域. 
@var ACTION_WINDOW_SELECTING: 正在选择区域.
@var ACTION_WINDOW_SELECTED: 已经选择,但是没有按下任何按钮  
'''
ACTION_WINDOW_INIT = 0
ACTION_WINDOW_SELECTING = 1
ACTION_WINDOW_SELECTED = 2


'''
拖动鼠标的状态.
@var DRAG_INSIDE: 光标在区域内.
@var DRAG_OUTSIDE: 光标在区域外.
@var DRAG_TOP_LEFT_CORNER: 光标在区域左上方.
@var DRAG_TOP_RIGHT_CORNER: 光标在区域右上方.
@var DRAG_BOTTOM_LEFT_CORNER: 光标在区域左下方.
@var DRAG_BOTTOM_RIGHT_CORNER: 光标在区域右下方.
@var DRAG_TOP_SIDE: 光标在区域顶部.
@var DRAG_BOTTOM_SIDE: 光标在区域底部.
@var DRAG_LEFT_SIDE: 光标在区域左侧
@var DRAG_RIGHT_SIDE: 光标在区域右侧.
'''
DRAG_INSIDE = 10
DRAG_OUTSIDE = 11
DRAG_TOP_LEFT_CORNER = 12
DRAG_TOP_RIGHT_CORNER = 13
DRAG_BOTTOM_LEFT_CORNER = 14
DRAG_BOTTOM_RIGHT_CORNER = 15
DRAG_TOP_SIDE = 16
DRAG_BOTTOM_SIDE = 17
DRAG_LEFT_SIDE = 18
DRAG_RIGHT_SIDE = 19

'''
cairo线宽值用来显示线的粗细
@var ACTION_CAIRO_WIDTH_SIZE_SMALL: 小宽度.
@var ACTION_CAIRO_WIDTH_SIZE_NORMAL: 正常宽度.
@var ACTION_CAIRO_WIDTH_SIZE_BIG: 大宽度.
'''
ACTION_SIZE_SMALL = 2
ACTION_SIZE_NORMAL = 3
ACTION_SIZE_BIG = 5

'''
放大镜的位置.
@var MAGNIFIER_POS_LEFT: 光标在屏幕左侧.
@var MAGNIFIER_POS_RIGHT: 光标在屏幕右侧.
@var MAGNIFIER_POS_TOP: 光标在屏幕上方.
@var MAGNIFIER_POS_BOTTOM: 光标在屏幕底部.
'''
MAGNIFIER_POS_LEFT = (1<<0)  #对应的值为1 二进制来计算的
MAGNIFIER_POS_RIGHT= (1<<1) #对应的值为2
MAGNIFIER_POS_TOP= (1<<2) #对应的值为4
MAGNIFIER_POS_BOTTOM= (1<<3) #对应的值为8

'''
@var BUTTON_EVENT_LEFT: 鼠标左键事件
@var BUTTON_EVENT_MIDDLE: 鼠标中键事件
@var BUTTON_EVENT_RIGHT: 鼠标右键事件
'''
BUTTON_EVENT_LEFT = 1
BUTTON_EVENT_MIDDLE = 2
BUTTON_EVENT_RIGHT = 3


'''
@var SCREENSHOT_MODE_NORMAL: 一般模式
@var SCREENSHOT_MODE_FULLSCREEN: 全屏模式
@var SCREENSHOT_MODE_WINDOW: 窗口模式
'''
SCREENSHOT_MODE_NORMAL = 0
SCREENSHOT_MODE_FULLSCREEN = 1
SCREENSHOT_MODE_WINDOW = 2

'''
@var DEFAULT_FILENAME: 保存的默认文件名.
@var DEFAULT_FONT: 默认字体.
'''
DEFAULT_FILENAME = "NFS"
DEFAULT_FONT = "文泉驿正黑"

'''
保存操作 修改了原来的显示字段，使之更加清楚
@var SAVE_OPERATION_AUTO: 自动保存.
@var SAVE_OPERATION_AS: 自定义文件保存.
@var SAVE_OPERATION_CLIP: 保存到剪贴板.
@var SAVE_OPERATION_AUTO_AND_CLIP: 自动保存，同时保存一份到剪贴板中.
@var SAVE_OPERATION_MAX_NUM: 保存操作最大的操作次数.
'''
SAVE_OPERATION_AS = 0
SAVE_OPERATION_AUTO = 1
SAVE_OPERATION_CLIP = 2
SAVE_OPERATION_AUTO_AND_CLIP = 3
SAVE_OPERATION_MAX_NUM = 4
