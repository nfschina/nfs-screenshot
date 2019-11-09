#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#
#Copyright (c) 2016-2018 CPU and Fundamental Software Research Center,CAS
#Based on code from src/window.py in deepin-screenshot-2.0
# Copyright (C) 2011 Deepin, Inc.
#               2011 Hou Shaohui
#
# Author:     Hou Shaohui <houshao55@gmail.com>
#             Long Changjin <admin@longchangjin.cn>
# Maintainer: Hou ShaoHui <houshao55@gmail.com>
#             Long Changjin <admin@longchangjin.cn>
#This software is published by the license of CPU-OS License,you can use and 
#distibuted this software under this License.See CPU-OS Liense for more detail.
#You should have receive a copy of CPU-OS License.If not.please contact us 
#by email <support_os@cpu-os.ac.cn> 

from collections import namedtuple
import pygtk
pygtk.require("2.0")
import gtk
import wnck
from Xlib import display, Xatom
import sys
import os

from nfs_common import get_format_time, get_pictures_dir, parser_path
from nfs_constant import DEFAULT_FILENAME


DISPLAY_NUM = len(gtk.gdk.display_manager_get().list_displays())    # 显示屏数量
DISPLAY = gtk.gdk.display_get_default()         # 当前显示屏
SCREEN_NUM = DISPLAY.get_n_screens()            # gtk.gdk.Screen num
GDK_SCREEN = DISPLAY.get_default_screen()       # gtk.gdk.Screen
MONITOR_NUM = GDK_SCREEN.get_n_monitors()       # the monitors number

CURRENT_MONITOR = 0                             # index of current monitor
CURRENT_MONITOR_INFO = GDK_SCREEN.get_monitor_geometry(CURRENT_MONITOR) # current monitor info
SCREEN_WIDTH = CURRENT_MONITOR_INFO.width       # current monitor width
SCREEN_HEIGHT = CURRENT_MONITOR_INFO.height     # current monitor height
SCREEN_X = CURRENT_MONITOR_INFO.x               # current monitor x coordinate
SCREEN_Y = CURRENT_MONITOR_INFO.y               # current monitor y coordinate

WNCK_SCREEN = wnck.screen_get_default()         # wnck.Screen
WNCK_SCREEN.force_update()                      # update wnc.Screen
WNCK_WORKSPACE = WNCK_SCREEN.get_active_workspace() # current workspace

# for multi monitor, get current monitor
def get_current_monitor():
    '''
    get current monitor
    @return: the index of current monitor
    '''
    global CURRENT_MONITOR
    CURRENT_MONITOR = GDK_SCREEN.get_monitor_at_point(*DISPLAY.get_pointer()[1:3])
    return CURRENT_MONITOR

def get_current_monitor_info():
    '''
    get current monitor geometry
    @return: a tuple containing the X and Y coordinate and width and height of current monitor
    '''
    global CURRENT_MONITOR_INFO
    global SCREEN_X, SCREEN_Y, SCREEN_WIDTH, SCREEN_HEIGHT
    CURRENT_MONITOR_INFO = GDK_SCREEN.get_monitor_geometry(get_current_monitor())
    SCREEN_WIDTH = CURRENT_MONITOR_INFO.width
    SCREEN_HEIGHT = CURRENT_MONITOR_INFO.height
    SCREEN_X = CURRENT_MONITOR_INFO.x
    SCREEN_Y = CURRENT_MONITOR_INFO.y
    return CURRENT_MONITOR_INFO

def convert_coord(x, y, width, height):
    '''
    cut out overstep the monitor
    @param x: X coordinate of the source point
    @param y: Y coordinate of the source point
    @param width: the area's width
    @param height: the area's height
    @return: a tuple containing new x and y and width and height that in this monitor
    '''
    end_x = x + width - SCREEN_X
    end_y = y + height - SCREEN_Y
    # overstep left of monitor
    if x < SCREEN_X:
        width += x - SCREEN_X
        x = SCREEN_X
    # overstep top of monitor
    if y < SCREEN_Y:
        height += y - SCREEN_Y
        y = SCREEN_Y
    # overstep right of monitor
    if end_x > SCREEN_WIDTH:
        width = SCREEN_WIDTH - x
    # overstep bottom of monitor
    if end_y > SCREEN_HEIGHT:
        height = SCREEN_HEIGHT - y
    return (x, y, width, height)

def get_screenshot_window_info():
    '''
    get current monitor windows info
    @return: all windows' coordinate in this workspace
    @rtype: a list, each in the list is a tuple which containing x and y and width and height
    '''
    get_current_monitor_info()
    return get_windows_info()

def get_windows_info():
    '''
    @return: all windows' coordinate in this workspace
    @rtype: a list, each in the list is a tuple which containing x and y and width and height
    '''
    coord= namedtuple('coord', 'x y width height')
    screenshot_window_info = []
    screenshot_window_info.insert(0, coord(SCREEN_X, SCREEN_Y, SCREEN_WIDTH, SCREEN_HEIGHT))
    WNCK_SCREEN.force_update()
    win_list = WNCK_SCREEN.get_windows_stacked()
    global WNCK_WORKSPACE
    WNCK_WORKSPACE = WNCK_SCREEN.get_active_workspace()
    if not WNCK_WORKSPACE:      # there is no active workspace in some wm.
        WNCK_WORKSPACE = WNCK_SCREEN.get_workspaces()[0]
    for w in win_list:
        if not w.is_on_workspace(WNCK_WORKSPACE):
            continue
        try:    # some environment has not WINDOW_STATE_MINIMIZED property
            if w.get_state() & wnck.WINDOW_STATE_MINIMIZED or\
                    w.get_state() & wnck.WINDOW_STATE_HIDDEN or\
                    w.get_window_type() == wnck.WINDOW_DESKTOP:
                continue
        except:
            pass
        (x, y, width, height) = w.get_geometry()                # with frame
        #(x, y, width, height) = w.get_client_window_geometry()  # without frame

        # Get shadow value for window.
        nfs_window_shadow_value = get_window_property_by_id(w.get_xid(), "NFS_WINDOW_SHADOW")
        if nfs_window_shadow_value:
            nfs_window_shadow_size = int(nfs_window_shadow_value)
        else:
            nfs_window_shadow_size = 0

        if w.get_window_type() == wnck.WINDOW_DOCK and\
                width >= SCREEN_WIDTH and height >= SCREEN_HEIGHT:
            continue
        screenshot_window_info.insert(0, coord(*convert_coord(
                    x + nfs_window_shadow_size,
                    y + nfs_window_shadow_size,
                    width - nfs_window_shadow_size * 2,
                    height - nfs_window_shadow_size * 2)))
    return screenshot_window_info

def get_window_info_at_pointer():
    '''
    获取鼠标所在位置的窗口
    return: a tuple containing x and y and width and height of the window at pointer
    '''
    (x, y) = DISPLAY.get_pointer()[1:3]
    win_info = get_screenshot_window_info()
    for info in win_info:
        if info.x <= x <= info.x + info.width and info.y <= y <= info.y + info.height:
            return info
        
def get_window_info_currentActive():
    '''
    获取当前活动的窗口
    return: a tuple containing x and y and width and height of the window at pointer
    '''
    win_info = get_screenshot_window_info()
    return win_info[0];
     

def get_screenshot_pixbuf(fullscreen=True):
    '''
    全屏截图
    @param fullscreen: if get fullscreen snapshot.
    @return: a gtk.gdk.Pixbuf of screenshot
    '''
    xroot = display.Display().screen().root
    root_window = gtk.gdk.window_foreign_new(xroot.id)
    if not fullscreen:
        '''获取光标所在位置窗口'''
        #info = get_window_info_at_pointer()
        '''获取当前活动窗口'''
        info = get_window_info_currentActive()
        (x, y, width, height) = (info.x, info.y, info.width, info.height)
    else:
        (x, y, width, height) = get_current_monitor_info()

    pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, width, height)
    pixbuf.get_from_drawable(root_window, root_window.get_colormap(), x, y, 0, 0, width, height)
    return pixbuf


#
def get_display(index):
    '''
    get the index display
    @param index: the index of display
    '''
    if index >= DISPLAY_NUM:
        return
    global DISPLAY
    global SCREEN_NUM
    DISPLAY = gtk.gdk.display_manager_get().list_displays()[index]
    SCREEN_NUM = DISPLAY.get_n_screens()

def get_wnck_screen(index):
    '''
    get the index screen
    @param index: the index of screen
    '''
    global WNCK_SCREEN
    screen = wnck.screen_get(index)
    if screen:
        WNCK_SCREEN = screen
        WNCK_SCREEN.force_update()

        global WNCK_WORKSPACE
        global SCREEN_WIDTH
        global SCREEN_HEIGHT
        WNCK_WORKSPACE = WNCK_SCREEN.get_active_workspace()
        SCREEN_WIDTH = WNCK_SCREEN.get_width()
        SCREEN_HEIGHT = WNCK_SCREEN.get_height()
    if index >= SCREEN_NUM:
        return
    global GDK_SCREEN
    GDK_SCREEN = DISPLAY.get_screen(index)


xlib_display = None

def init_xlib(func):
    global xlib_display

    if xlib_display == None:
        xlib_display =  display.Display()

    def wrap(*a, **kw):
        ret = func(*a, **kw)
        return ret

    return wrap

@init_xlib
def get_window_by_id(win_id):
    return xlib_display.create_resource_object("window", win_id)

@init_xlib
def set_window_property(xwindow, property_type, property_content):
    xwindow.change_property(
        xlib_display.get_atom(property_type),
        Xatom.STRING,
        8,
        property_content,
        )
    xlib_display.sync()

@init_xlib
def get_window_property(xwindow, property_type):
    try:
        return xwindow.get_full_property(
            xlib_display.get_atom(property_type),
            Xatom.STRING
            ).value
    except:
        return None

def set_window_property_by_id(window_id, property_type, property_content):
    set_window_property(get_window_by_id(window_id), property_type, property_content)

def get_window_property_by_id(window_id, property_type):
    return get_window_property(get_window_by_id(window_id), property_type)



if __name__ == '__main__':
    '''截图全屏'''
#     pixbuf = get_screenshot_pixbuf()
#     #自动保存到指定目录
#     filename = "%s/%s%s.%s" % (get_pictures_dir(), DEFAULT_FILENAME,
#                                get_format_time(), "png")
#     pixbuf.save(filename, "png")

     #1的话代表截取全屏
    _length = len(sys.argv)
    sStr1 = sys.argv[1]
    sStr2 = '1' 
    #参数2是用来判断当前是否是printscreen键触发的（在软件没有启动的情况下，默认流程是先保存图片，在进行判断操作）,为0表示print键触发
    sStr3 = '1'
    if( _length-1 >= 2 ):
	 sStr3 = sys.argv[2]
    
    if(cmp(sStr1,sStr2)): #不是1的话
	#截取当前活动窗口
        pixbuf = get_screenshot_pixbuf(False)
    else:
        #截取当前全屏
        pixbuf = get_screenshot_pixbuf(True) 
    if( _length-1 >= 3 ):
	    print '33333'
	    clipboard = gtk.Clipboard(selection="CLIPBOARD")
	    clipboard.set_image(pixbuf)
	    clipboard.store()
    else:
	    sStr4 ='0'
	    #自动保存到指定目录
	    #若文件夹不存在自动创建
	    if(cmp(sStr3,sStr4)):    #这个默认返回的是0
		b = os.path.exists(get_pictures_dir()+'/.nfs')
		if(b == 0):
			os.mkdir(get_pictures_dir()+'/.nfs')
		filename = "%s/%s%s.%s" % (get_pictures_dir()+'/.nfs', DEFAULT_FILENAME,
				               get_format_time(), "png")
		pixbuf.save(filename, "png")
	    else:	
		b = os.path.exists(get_pictures_dir()+'/.nfsprint')
		if(b == 0):
			os.mkdir(get_pictures_dir()+'/.nfsprint')
		filename = "%s/%s%s.%s" % (get_pictures_dir()+'/.nfsprint', DEFAULT_FILENAME,
				               get_format_time(), "png")
		pixbuf.save(filename, "png")
	    print filename




