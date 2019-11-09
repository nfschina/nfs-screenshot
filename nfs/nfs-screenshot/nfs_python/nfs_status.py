#!/usr/bin/python
#-*- coding:utf-8 -*-
#Copyright (c) 2016-2018 CPU and Fundamental Software Research Center,CAS
#Based on code from src/status.py in deepin-screenshot-2.0
# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>
#This software is published by the license of CPU-OS License,you can use and 
#distibuted this software under this License.See CPU-OS Liense for more detail.
#You should have receive a copy of CPU-OS License.If not,please contact us 
#by email <support_os@cpu-os.ac.cn>
#模块描述：
#   状态
#
#作者: liangjian
#日期：2014-08-20

from nfs_constant import *
import nfs_common
from nfs_draw import *

class BaseProcess(object):
    ''' BaseProcess Class. it must be inherited and refactored'''
    def __init__(self, screenshot=None, window=None):
        '''
        init process
        @param screenshot: a Screenshot object
        @param window: a RootWindow object
        '''
        self.screenshot = screenshot
        self.win = window
        self.event = None
        self.func_map = {
            ACTION_WINDOW_SELECTING: self.action_init,
            ACTION_WINDOW_SELECTED: self.action_select,
            ACTION_WINDOW_INIT: self.action_window,
            None: self._none_action}

    def update(self, event):
        '''
        update event info
        @param event: a gtk.gdk.Event
        '''
        self.event = event

    def action_init(self, screenshot, event):
        '''
        process the in event in ACTION_INIT status
        @param screenshot: a Screenshot object
        @param event: a gtk.gdk.Event
        '''
        pass


    def action_select(self, screenshot, event):
        '''
        process the in event in ACTION_SELECT status
        @param screenshot: a Screenshot object
        @param event: a gtk.gdk.Event
        '''
        pass


    def action_window(self, screenshot, event):
        '''
        process the in event in ACTION_WINDOW status
        @param screenshot: a Screenshot object
        @param event: a gtk.gdk.Event
        '''
        pass

    def _none_action(self, *arg):
        ''' process the in event in Action None status '''
        pass

class ButtonPressProcess(BaseProcess):
    ''' buton press status class'''
    def __init__(self, screenshot=None, window=None):
        BaseProcess.__init__(self, screenshot, window)

    def process(self):
        '''Press process button press event'''
        if self.event is None:
            return
        if self.event.button == BUTTON_EVENT_LEFT:
            self.screenshot.drag_flag = True
            self.func_map[self.screenshot.action](self.screenshot, self.event)
            
        elif self.event.button == BUTTON_EVENT_RIGHT:
            ev = self.event
            screenshot = self.screenshot
            if screenshot.window_flag:  # has not select area, press right button quit
                self.win.quit()
            else:    
                if is_in_rect((ev.x_root, ev.y_root), screenshot.get_rectangel()) == False:

                    while screenshot.action_list:
                        screenshot.action_list.pop()
                    while screenshot.text_action_list:
                        screenshot.text_action_list.pop()
                    screenshot.text_action_info.clear()
                    screenshot.undo()

    def action_window(self, screenshot, event):
        '''Press ACTION_WINDOW '''
        screenshot.window_flag = False

    def action_init(self, screenshot, event):
        '''Press ACTION_INIT '''
        (screenshot.x, screenshot.y) = self.win.get_event_coord(event)

    def action_select(self, screenshot, event):
        '''Press ACTION_SELECT '''
        # Init drag position.
        screenshot.drag_position = self.win.get_position(event)
        # Set cursor.
        self.win.set_cursor(screenshot.drag_position)
        # Get drag coord and offset.
        (screenshot.dragStartX, screenshot.dragStartY) = self.win.get_event_coord(event)
        screenshot.dragStartOffsetX = screenshot.dragStartX - screenshot.x
        screenshot.dragStartOffsetY = screenshot.dragStartY - screenshot.y




class ButtonReleaseProcess(BaseProcess):
    ''' button release process'''
    def __init__(self, screenshot=None, window=None):
        BaseProcess.__init__(self, screenshot, window)

    def process(self):
        '''Release process button release event'''
        if self.event is None:
            return
        if self.event.button == BUTTON_EVENT_LEFT:
            self.screenshot.text_drag_flag = False
            self.screenshot.drag_flag = False
            self.func_map[self.screenshot.action](self.screenshot, self.event)
            

    def action_window(self, screenshot, event):
        '''Release ACTION_WINDOW'''
        if screenshot.rect_width > 5 and screenshot.rect_height > 5:
#             self.win.show_toolbar()
#             self.win.adjust_toolbar()
            screenshot.action = ACTION_WINDOW_SELECTED
            self.win.refresh()
        else:
            screenshot.window_flag = True

    def action_init(self, screenshot, event):
        '''Release ACTION_INIT'''
        screenshot.action = ACTION_WINDOW_SELECTED
        (ex, ey) = self.win.get_event_coord(event)
        # Adjust rectangle when button release.
        if ex > screenshot.x:
            screenshot.rect_width = ex - screenshot.x
        else:
            screenshot.rect_width = abs(ex - screenshot.x)
            screenshot.x = max(ex, screenshot.monitor_x)
        if ey > screenshot.y:
            screenshot.rect_height = ey - screenshot.y
        else:
            screenshot.rect_height = abs(ey - screenshot.y)
            screenshot.y = max(ey, screenshot.monitor_y)
        # min rect 2 * 2
        if screenshot.rect_width < 2:
            screenshot.rect_width = 2
            if screenshot.rect_width + screenshot.x > screenshot.width:
                screenshot.x = screenshot.width - screenshot.rect_width
        if screenshot.rect_height < 2:
            screenshot.rect_height = 2
            if screenshot.rect_height + screenshot.y > screenshot.height:
                screenshot.y = screenshot.height - screenshot.rect_height

        self.win.refresh()
        #self.win.show_toolbar()
        #self.win.adjust_toolbar()

    def action_select(self, screenshot, event):
        '''Release ACTION_SELECT '''
        # min rect 2 * 2
        if screenshot.rect_width < 2:
            screenshot.rect_width = 2
            if screenshot.rect_width + screenshot.x > screenshot.width:
                screenshot.x = screenshot.width - screenshot.rect_width
        if screenshot.rect_height < 2:
            screenshot.rect_height = 2
            if screenshot.rect_height + screenshot.y > screenshot.height:
                screenshot.y = screenshot.height - screenshot.rect_height
        self.win.refresh()

    


class MotionProcess(BaseProcess):
    ''' Motion process'''
    def __init__(self, screenshot=None, window=None):
        BaseProcess.__init__(self, screenshot, window)

    def process(self):
        '''Motion process motion event'''
        if self.event is None:
            return
        self.func_map[self.screenshot.action](self.screenshot, self.event)
        self.adjust(self.screenshot, self.event)

    def action_window(self, screenshot, event):
        '''Motion ACTION_WINDOW'''
        # can drag and has selected area
        if screenshot.drag_flag and not screenshot.window_flag:
            (ex, ey) = self.win.get_event_coord(event)
            screenshot.action = ACTION_WINDOW_SELECTING
            (screenshot.x, screenshot.y) = self.win.get_event_coord(event)
            self.win.refresh()
        else:   # update magnifier
            size = "%d x %d " % (screenshot.rect_width, screenshot.rect_height)
            rgb = nfs_common.get_coord_rgb(screenshot, event.x, event.y)
            self.win.update_magnifier(event.x, event.y, size=size, rgb=str(rgb))

    def action_init(self, screenshot, event):
        '''Motion ACTION_INIT'''
        if screenshot.drag_flag:
            (ex, ey) = self.win.get_event_coord(event)
            (screenshot.rect_width, screenshot.rect_height) = (ex - screenshot.x, ey - screenshot.y)
            self.win.refresh()

    def action_select(self, screenshot, event):
        '''Motion ACTION_SELECT '''
        # drag the selected area
        if screenshot.drag_flag:
            (ex, ey) = self.win.get_event_coord(event)
            if screenshot.drag_position == DRAG_INSIDE:
                screenshot.x = min(max(ex - screenshot.dragStartOffsetX, screenshot.monitor_x),
                    screenshot.monitor_x + screenshot.width - screenshot.rect_width)
                screenshot.y = min(max(ey - screenshot.dragStartOffsetY, screenshot.monitor_y),
                    screenshot.monitor_y + screenshot.height - screenshot.rect_height)
            elif screenshot.drag_position == DRAG_TOP_SIDE:
                self.win.drag_frame_top(ex, ey)
            elif screenshot.drag_position == DRAG_BOTTOM_SIDE:
                self.win.drag_frame_bottom(ex, ey)
            elif screenshot.drag_position == DRAG_LEFT_SIDE:
                self.win.drag_frame_left(ex, ey)
            elif screenshot.drag_position == DRAG_RIGHT_SIDE:
                self.win.drag_frame_right(ex, ey)
            elif screenshot.drag_position == DRAG_TOP_LEFT_CORNER:
                self.win.drag_frame_top(ex, ey)
                self.win.drag_frame_left(ex, ey)
            elif screenshot.drag_position == DRAG_TOP_RIGHT_CORNER:
                self.win.drag_frame_top(ex, ey)
                self.win.drag_frame_right(ex, ey)
            elif screenshot.drag_position == DRAG_BOTTOM_LEFT_CORNER:
                self.win.drag_frame_bottom(ex, ey)
                self.win.drag_frame_left(ex, ey)
            elif screenshot.drag_position == DRAG_BOTTOM_RIGHT_CORNER:
                self.win.drag_frame_bottom(ex, ey)
                self.win.drag_frame_right(ex, ey)

            self.win.refresh()
        else:
            screenshot.drag_position = self.win.get_position(event)
            # to avoid set cursor again
            if screenshot.last_drag_position != screenshot.drag_position:
                screenshot.last_drag_position = screenshot.drag_position
                self.win.set_cursor(screenshot.drag_position)



    def adjust(self, screenshot, event):
        '''Motion adjust '''
        # can't drag and has not selected area
        if not screenshot.drag_flag and screenshot.window_flag:

            (wx, wy) = self.win.get_event_coord(event)
            for each in screenshot.screenshot_window_info:
                if each.x <= wx <= (each.x + each.width) and each.y <= wy <= (each.y + each.height):
                    screenshot.x = each.x
                    screenshot.y = each.y
                    screenshot.rect_width = each.width
                    screenshot.rect_height = each.height
                    break
            self.win.refresh()

 
