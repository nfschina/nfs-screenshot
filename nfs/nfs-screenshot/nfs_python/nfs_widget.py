#!/usr/bin/python
#-*- coding:utf-8 -*-
#Copyright (c) 2016-2018 CPU and Fundamental Software Research Center,CAS
#Based on code from src/widget.py in deepin-screenshot-2.0
# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>

#This software is published by the license of CPU-OS License，you can use and 
#distibuted this software under this License.See CPU-OS Liense for more detail.
#You should have receive a copy of CPU-OS License.If not,please contact us 
#by email <support_os@cpu-os.ac.cn>  
#
# zhuyun
#

from keymap import get_keyevent_name
from collections import namedtuple
from nfs_constant import *
from nfs_nls import _
import nfs_status
import gtk
import pango
import gobject
import threading
import time
import os
import nfs_common
from math import *
from nfs_draw import *


Magnifier = namedtuple('Magnifier', 'x y size_content tip rgb')

theme_cursor = {
    DRAG_INSIDE: gtk.gdk.Cursor(gtk.gdk.FLEUR),
    DRAG_OUTSIDE: None,
    DRAG_TOP_LEFT_CORNER: gtk.gdk.Cursor(gtk.gdk.TOP_LEFT_CORNER),
    DRAG_TOP_RIGHT_CORNER: gtk.gdk.Cursor(gtk.gdk.TOP_RIGHT_CORNER),
    DRAG_BOTTOM_LEFT_CORNER: gtk.gdk.Cursor(gtk.gdk.BOTTOM_LEFT_CORNER),
    DRAG_BOTTOM_RIGHT_CORNER: gtk.gdk.Cursor(gtk.gdk.BOTTOM_RIGHT_CORNER),
    DRAG_TOP_SIDE: gtk.gdk.Cursor(gtk.gdk.TOP_SIDE),
    DRAG_BOTTOM_SIDE: gtk.gdk.Cursor(gtk.gdk.BOTTOM_SIDE),
    DRAG_LEFT_SIDE: gtk.gdk.Cursor(gtk.gdk.LEFT_SIDE),
    DRAG_RIGHT_SIDE: gtk.gdk.Cursor(gtk.gdk.RIGHT_SIDE),
    ACTION_WINDOW_SELECTING: None,
    ACTION_WINDOW_INIT: gtk.gdk.Cursor(gtk.gdk.TCROSS),
#     ACTION_WINDOW_INIT: gtk.gdk.Cursor(gtk.gdk.display_get_default(), app_theme.get_pixbuf("start_cursor.png").get_pixbuf(), 0, 0),
    None: None}
theme_cursor['drag'] = theme_cursor[DRAG_INSIDE]

class RootWindow(object):
    ''' root window of the screenshot '''
    def __init__(self, screenshot):
        self.screenshot = screenshot            # screenshot类
        self.frame_border = 2                   # 边框宽度
        self.drag_point_radius = 4              # 画图圆点的半径
        self.__frame_color = (0.0, 0.68, 1.0)   # 边框颜色

        ''' 截图遮盖层 '''
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        # move window to current monitor
        self.window.move(self.screenshot.monitor_x, self.screenshot.monitor_y)
        self.window.fullscreen()   
        self.window.set_keep_above(True)
        #self.window.set_app_paintable(True)

        self.window.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.window.add_events(gtk.gdk.POINTER_MOTION_MASK)
        self.window.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.window.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.window.connect("destroy", self.quit)
        #self.window.connect("destroy", self.destroy_all)
        self.window.connect("button-press-event", self._button_press_event)
        
        self.window.connect("button-press-event", self._button_double_clicked)
        self.window.connect("button-release-event", self._button_release_event)
        self.window.connect("motion-notify-event", self._motion_notify_event)
        self.window.connect("key-press-event", self._key_press_event)
        self.window.connect("scroll-event", self._scroll_event)
        
        self.draw_area = gtk.Fixed()
        self.draw_area.connect("expose-event", self._draw_expose)
        self.window.add(self.draw_area)
        self.magnifier = None
        self.finish_flag = False
        
        '''绑定鼠标点击事件'''
        self._button_pressed_process = nfs_status.ButtonPressProcess(screenshot, self)
        self._button_released_process = nfs_status.ButtonReleaseProcess(screenshot, self)
        self._button_motion_process = nfs_status.MotionProcess(screenshot, self)

        '''设置快捷键'''                          
        self.hotkey_map = { "Escape": self.quit}
        if self.screenshot:
            self.hotkey_map["Ctrl + S"] = self._save_to_file
            self.hotkey_map["Return"] = self._key_enter_press
            self.hotkey_map["KP_Enter"] = self._key_enter_press
#             self.hotkey_map["Ctrl + Z"] = self.screenshot.undo
#             self.hotkey_map["Ctrl + z"] = self.hotkey_map["Ctrl + Z"]
            self.hotkey_map["Ctrl + s"] = self.hotkey_map["Ctrl + S"]
            self.hotkey_map["Up"] = self.move_area_up
            self.hotkey_map["Down"] = self.move_area_down
            self.hotkey_map["Left"] = self.move_area_left
            self.hotkey_map["Right"] = self.move_area_right
            self.hotkey_map["Ctrl + Up"] = self.extend_area_up
            self.hotkey_map["Ctrl + Down"] = self.extend_area_down
            self.hotkey_map["Ctrl + Left"] = self.extend_area_left
            self.hotkey_map["Ctrl + Right"] = self.extend_area_right

    def _draw_expose(self, widget, event):
        ''' 绘图区暴露事件回调，绘制背景与行动 '''
        cr = widget.window.cairo_create()
        # 画背景
        if self.screenshot:
            cr.set_source_pixbuf(self.screenshot.desktop_background, 0, 0)
            cr.paint()
        
        if self.finish_flag:
            return True
        # draw mask
        self._draw_mask(cr)


        # ACTION_WINDOW draw magnifier and window frame
        if self.magnifier and self.screenshot.action in [ACTION_WINDOW_SELECTING, ACTION_WINDOW_INIT]:
            '''放大镜'''
            self._draw_magnifier(cr)
            '''绘制窗口框架'''
            self._draw_window_rectangle(cr)
        
        if self.screenshot.action != ACTION_WINDOW_INIT:
            self._draw_frame(cr)
            self._draw_drag_point(cr)
            # 显示选中尺寸大小
            if self.screenshot.y - 35 > self.screenshot.monitor_y:  # convert coord
                size_tip_x = self.screenshot.x - self.screenshot.monitor_x + 5
                if size_tip_x + 90 > self.screenshot.width:
                    size_tip_x = self.screenshot.width - 90
                size_tip_y = self.screenshot.y - self.screenshot.monitor_y - 35
                draw_round_text_rectangle(cr, size_tip_x, size_tip_y, 90, 30, 7,
                    '%d x %d' % (fabs(self.screenshot.rect_width), fabs(self.screenshot.rect_height)), 0.7)
            elif self.screenshot.action in [None, ACTION_WINDOW_SELECTED, ACTION_WINDOW_INIT, ACTION_WINDOW_SELECTING]:
                size_tip_x = self.screenshot.x - self.screenshot.monitor_x + 5
                if size_tip_x + 90 > self.screenshot.width:
                    size_tip_x = self.screenshot.width - 90
                size_tip_y = self.screenshot.y - self.screenshot.monitor_y + 5
                draw_round_text_rectangle(cr, size_tip_x, size_tip_y, 90, 30, 7,
                    '%d x %d' % (fabs(self.screenshot.rect_width), fabs(self.screenshot.rect_height)), 0.7)
        # update text action info
        for each_text_action in self.screenshot.text_action_list:
            self.screenshot.text_action_info[each_text_action] = each_text_action.get_layout_info()
        

    def _button_press_event(self, widget, event):
        ''' button press event callback '''
        if self.screenshot is None:
            return
        self._button_pressed_process.update(event)
        self._button_pressed_process.process()
    
    def _button_double_clicked(self, widget, event):
        ''' double clicked '''
        if self.screenshot is None:
            return
        # double click
        (ex, ey) = self.get_event_coord(event)
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:

            # save snapshot
            if self.screenshot.action == ACTION_WINDOW_SELECTED \
               or self.screenshot.action == None \
               and self.screenshot.x < ex < self.screenshot.x + self.screenshot.rect_width \
               and self.screenshot.y < ey < self.screenshot.y + self.screenshot.rect_height:
                #self.screenshot.save_snapshot()
                release_event = gtk.gdk.Event(gtk.gdk.BUTTON_RELEASE)
                release_event.send_event = True
                release_event.button = event.button
                release_event.x = event.x
                release_event.y = event.y
                release_event.x_root = event.x_root
                release_event.y_root = event.y_root
                widget.event(release_event)
                #文件另存为
                self.save_to_file()
                
     
                
    def save_to_file(self):
        '''保存到文件，直接保存'''
        new_path = nfs_common.get_pictures_dir()+'/.nfs/'
        if not os.path.isdir(new_path):
            os.makedirs(new_path)
        self._save_to_file_cb(new_path+nfs_common.get_format_time()+'.png')        
            
    
    def save_to_file_as(self):
        ''' 保存到文件,另存为 '''
        #self.fresh_saveFiletype()
        #self.win.hide_colorbar()
        #self.win.hide_toolbar()
        #dialog = SaveFileDialog('', self.screenshot.window.window,
            #ok_callback=self._save_to_file_cb, cancel_callback=self._save_to_file_cancel)
        dialog = gtk.FileChooserDialog(
            "Save..",
            self.window,
            gtk.FILE_CHOOSER_ACTION_SAVE,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
             gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))
        dialog.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
        dialog.set_default_response(gtk.RESPONSE_ACCEPT)
        dialog.set_position(gtk.WIN_POS_MOUSE)
        dialog.set_local_only(True)
#         last_folder = self.__config.get("save", "folder")
#         if last_folder:
#             dialog.set_current_folder(last_folder)
#         else:
#             dialog.set_current_folder(nfs_common.get_pictures_dir())
        dialog.set_current_folder(nfs_common.get_pictures_dir())
        
        dialog.set_current_name("%s%s.%s" % (_(DEFAULT_FILENAME), nfs_common.get_format_time(), "png"))
        response = dialog.run()
        filename = dialog.get_filename()
        if response == gtk.RESPONSE_ACCEPT:
#             self.__config.set("save", folder=dialog.get_current_folder())
            self._save_to_file_cb(filename)
        #else:
         #   self._save_to_file_cancel(filename)
        dialog.destroy()
    
    
    def _save_to_file_cancel(self, filename):
        ''' save file dialog cancel_callback'''
        self.screenshot.share_to_flag = False
        self.win.adjust_toolbar()
        self.win.show_toolbar()
        if self.has_button_active():
            self.win.show_colorbar()

    def _save_to_file_cb(self, filename):
        ''' save file dialog ok_callback'''
        self.screenshot.save_snapshot(filename=filename)
    
    
    def _button_release_event(self, widget, event):
        ''' button release event callback '''
        if self.screenshot is None:
            return
        self._button_released_process.update(event)
        self._button_released_process.process()
    
    def _motion_notify_event(self, widget, event):
        ''' motion notify event callback '''
        size = "%d x %d " % (self.screenshot.rect_width, self.screenshot.rect_height)
        rgb = nfs_common.get_coord_rgb(self.screenshot, event.x, event.y)
        self.update_magnifier(event.x, event.y, size=size, rgb=str(rgb))
        
        if self.screenshot is None:
            return
        self._button_motion_process.update(event)
        self._button_motion_process.process()
    
    def _key_enter_press(self):
        '''enter key press'''
        if self.screenshot.action != ACTION_WINDOW_INIT:
            self.screenshot.toolbar.save_operate()
    
    def _key_press_event(self, widget, event):
        ''' key press event callback'''
        key = get_keyevent_name(event)
        if key in self.hotkey_map:
            self.hotkey_map[key]()
    
    def quit(self, widget=None):
        ''' window destroy callback, exit'''
        gtk.main_quit()


    def destroy_all(self, widget=None):
        ''' after save snapshot, destroy all window  '''
        self.window.destroy()
        #self.window.hide()
        #self.screenshot.toolbar.window.destroy()
        #self.screenshot.colorbar.window.destroy()
        #threading.Thread(target=self.exit_thread).start()

    def exit_thread(self):
        '''wait a little, and exit  '''
        time.sleep(0.5)
        gtk.gdk.threads_enter()
        self.window.destroy()
        gtk.gdk.threads_leave()

    def update_magnifier(self, x, y, size='', tip="", rgb="RGB:(255,255,255)"):
        '''
        update magnifier
        @param x: the X coordinate of cursor point
        @param y: the Y coordinate of cursor point
        @param size: the window info at point, a string type
        @param tip: the tips shown, a string type
        @param rgb: the pixel's rgb at point, a string type
        '''
        self.magnifier = Magnifier(x, y, size, tip, rgb)

    def _draw_magnifier(self, cr):
        '''
        draw the magnifier
        @param cr: a gtk.gdk.CairoContext
        '''
        screen_width = self.screenshot.width
        screen_height = self.screenshot.height
        mag_width = pixbuf_width = 30
        mag_height = pixbuf_height = 20
        x = self.magnifier.x
        y = self.magnifier.y
        position = 0

        # the magnifier offset pos for pointor
        if screen_height - y < 168:
            offset_y = -34
        else:
            offset_y = 8
        if screen_width - x < 142:
            offset_x = -33
        else:
            offset_x = 3

        src_x = x - mag_width / 2
        src_y = y - mag_height / 2
        if src_x < 0:                               # position LEFT
            position |= MAGNIFIER_POS_LEFT
            pixbuf_width += src_x
            src_x = 0
        elif src_x > screen_width - pixbuf_width:   # position RIGHT
            position |= MAGNIFIER_POS_RIGHT
            pixbuf_width = screen_width - src_x
        else:
            src_x = fabs(src_x)                     # position middle
        if src_y < 0:                               # position TOP
            position |= MAGNIFIER_POS_TOP
            pixbuf_height += src_y
            src_y = 0
        elif src_y > screen_height - pixbuf_height:  # position BOTTOM
            position |= MAGNIFIER_POS_BOTTOM
            pixbuf_height = screen_height - src_y
        else:
            src_y = fabs(src_y)                     # position middle
        pixbuf = self.screenshot.desktop_background.subpixbuf(
            int(src_x), int(src_y), int(pixbuf_width), int(pixbuf_height))
        
        origin_x = offset_x + x
        origin_y = offset_y + y
        if position & MAGNIFIER_POS_LEFT:
            origin_x += (mag_width - pixbuf_width)
        if position & MAGNIFIER_POS_TOP:
            origin_y += (mag_height - pixbuf_height)
        #set zoom scale and translate
        cr.save()
        cr.translate(0 - 3 * x, 0 - 3 * y)
        cr.scale(4.0, 4.0)
        
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.8)
        cr.rectangle(x + offset_x - 1, y + offset_y - 1, mag_width + 2, mag_height + 14)
        cr.fill()
        
        #draw magnifier
        cr.set_line_width(1)
        cr.set_source_rgb(1, 1, 1)
        #cr.transform(matrix)
        cr.rectangle(x + offset_x, y + offset_y, mag_width, mag_height)
        cr.stroke_preserve()
        #cr.set_source_pixbuf(pixbuf, x + offset_x, y + offset_y)
        cr.set_source_pixbuf(pixbuf, origin_x, origin_y)
        #cr.set_source_pixbuf(pixbuf.scale_simple(int(pixbuf_width)*4,
            #int(pixbuf_height)*4, gtk.gdk.INTERP_BILINEAR), origin_x, origin_y)
        cr.fill()
        
        #draw Hline
        cr.set_line_width(1.2)
        cr.set_source_rgba(0, 0.7, 1.0, 0.5)
        cr.move_to(x + offset_x, y + offset_y + mag_height / 2)
        cr.line_to(x + offset_x + mag_width, y + offset_y + mag_height / 2)
        cr.stroke()
        
        #draw Vline
        cr.move_to(x + offset_x + mag_width / 2, y + offset_y)
        cr.line_to(x + offset_x + mag_width / 2, y + mag_height + offset_y)
        cr.stroke()
        
        draw_font(cr, self.magnifier.size_content, 3.0, "#FFFFFF", x + offset_x, y + offset_y + mag_height + 4)
        draw_font(cr, self.magnifier.rgb, 3.0, "#FFFFFF", x + offset_x, y + offset_y + mag_height + 7.5)
        draw_font(cr, self.magnifier.tip, 3.0, "#FFFFFF", x + offset_x, y + offset_y + mag_height + 11)
        cr.restore()
    
    def refresh(self):
        ''' refresh this window'''
        if self.screenshot.action_list:
            self.draw_area.queue_draw_area(*self.screenshot.get_rectangel_in_monitor())
        else:
            self.draw_area.queue_draw()

    def _draw_mask(self, cr):
        '''
        draw mask
        @param cr: a gtk.gdk.CairoContext
        '''
        if self.screenshot is None:
            return
        screenshot = self.screenshot
        # Adjust value when create selection area.
        # convert value in the monitor
        if screenshot.rect_width > 0:
            x = screenshot.x - screenshot.monitor_x
            rect_width = screenshot.rect_width
        else:
            x = screenshot.x - screenshot.monitor_x + screenshot.rect_width
            rect_width = abs(screenshot.rect_width)

        if screenshot.rect_height > 0:
            y = screenshot.y - screenshot.monitor_y
            rect_height = screenshot.rect_height
        else:
            y = screenshot.y - screenshot.monitor_y + screenshot.rect_height
            rect_height = abs(screenshot.rect_height)
        
        # Draw top.
        cr.set_source_rgba(0, 0, 0, 0.5)
        cr.rectangle(0, 0, screenshot.width, y)
        cr.fill()

        # Draw bottom.
        cr.set_source_rgba(0, 0, 0, 0.5)
        cr.rectangle(0, y + rect_height, screenshot.width, screenshot.height - y - rect_height)
        cr.fill()

        # Draw left.
        cr.set_source_rgba(0, 0, 0, 0.5)
        cr.rectangle(0, y, x, rect_height)
        cr.fill()

        # Draw right.
        cr.set_source_rgba(0, 0, 0, 0.5)
        cr.rectangle(x + rect_width, y, screenshot.width - x - rect_width, rect_height)
        cr.fill()

    def _draw_drag_point(self, cr):
        '''
        Draw drag point.
        @param cr: a gtk.gdk.CairoContext
        '''
        screenshot = self.screenshot
        cr.set_source_rgb(*self.__frame_color)
        # convert to coord in this monitor
        (x, y, width, height) = screenshot.get_rectangel_in_monitor()
        # Draw left top corner.
        cr.arc(x, y, self.drag_point_radius, 0, 2 * pi)
        cr.fill()
        # Draw right top corner.
        cr.arc(x + width, y, self.drag_point_radius, 0, 2 * pi)
        cr.fill()
        # Draw left bottom corner.
        cr.arc(x, y + height, self.drag_point_radius, 0, 2 * pi)
        cr.fill()
        # Draw right bottom corner.
        cr.arc(x + width, y + height, self.drag_point_radius, 0, 2 * pi)
        cr.fill()
        # Draw top side.
        cr.arc(x + width / 2, y, self.drag_point_radius, 0, 2 * pi)
        cr.fill()
        # Draw bottom side.
        cr.arc(x + width / 2, y + height, self.drag_point_radius, 0, 2 * pi)
        cr.fill()
        # Draw left side.
        cr.arc(x, y + height / 2, self.drag_point_radius, 0, 2 * pi)
        cr.fill()
        # Draw right side.
        cr.arc(x + width, y + height / 2, self.drag_point_radius, 0, 2 * pi)
        cr.fill()

    def _draw_frame(self, cr):
        '''
        Draw frame.
        @param cr: a gtk.gdk.CairoContext
        '''
        screenshot = self.screenshot
        cr.set_source_rgb(*self.__frame_color)
        cr.set_line_width(self.frame_border)
        #cr.rectangle(screenshot.x, screenshot.y, screenshot.rect_width, screenshot.rect_height)
        cr.rectangle(*screenshot.get_rectangel_in_monitor())
        cr.stroke()

    def _draw_window_rectangle(self, cr):
        '''
        Draw window frame.
        @param cr: a gtk.gdk.CairoContext
        '''
        screenshot = self.screenshot
        cr.set_line_width(4.5)
        cr.set_source_rgb(*(self.__frame_color))
        rect = screenshot.get_rectangel_in_monitor()
        cr.rectangle(rect[0] + 1, rect[1] + 1, rect[2] - 2, rect[3] - 2)
        cr.stroke()
    
    def get_event_coord(self, event):
        '''
        Get event coord.
        @param event: a gtk.gdk.Event
        @return: a tuple containing the event x_root and y_root
        '''
        (rx, ry) = event.get_root_coords()
        return (int(rx), int(ry))
    
    def get_event_coord_in_monitor(self, event):
        '''
        Get event coord in current monitor
        @param event: a gtk.gdk.Event
        @return: a tuple containing the event x_root and y_root in this monitor
        '''
        (ex, ey) = self.get_event_coord(event)
        return (ex-self.screenshot.monitor_x, ey-self.screenshot.monitor_y)
        
    def drag_frame_top(self, ex, ey):
        '''
        Drag frame top.
        @param ex: the X coordinate of the drag event
        @param ey: the Y coordinate of the drag event
        '''
        screenshot = self.screenshot
        maxY = screenshot.y + screenshot.rect_height
        screenshot.rect_height = screenshot.rect_height - min(screenshot.rect_height, (ey - screenshot.y))
        screenshot.y = min(ey, maxY) 
    
    def drag_frame_bottom(self, ex, ey):
        '''
        Drag frame bottom.
        @param ex: the X coordinate of the drag event
        @param ey: the Y coordinate of the drag event
        '''
        screenshot = self.screenshot
        screenshot.rect_height = max(0, ey - screenshot.y)
    
    def drag_frame_left(self, ex, ey):
        '''
        Drag frame left.
        @param ex: the X coordinate of the drag event
        @param ey: the Y coordinate of the drag event
        '''
        screenshot = self.screenshot
        maxX = screenshot.x + screenshot.rect_width
        screenshot.rect_width = screenshot.rect_width - min(screenshot.rect_width, (ex - screenshot.x))
        screenshot.x = min(ex, maxX)
    
    def drag_frame_right(self, ex, ey):
        '''
        Drag frame right.
        @param ex: the X coordinate of the drag event
        @param ey: the Y coordinate of the drag event
        '''
        screenshot = self.screenshot
        screenshot.rect_width = max(0, ex - screenshot.x)

    def get_drag_point_coords(self):
        '''
        Get drag point coords.
        @return: a 8-tuple containing the eight drag points' coords
        '''
        screenshot = self.screenshot
        return (
            # Top left.
            (screenshot.x - self.drag_point_radius, screenshot.y - self.drag_point_radius),
            # Top right.
            (screenshot.x + screenshot.rect_width - self.drag_point_radius, screenshot.y - self.drag_point_radius),
            # Bottom left.
            (screenshot.x - self.drag_point_radius, screenshot.y + screenshot.rect_height - self.drag_point_radius),
            # Bottom right.
            (screenshot.x + screenshot.rect_width - self.drag_point_radius, screenshot.y + screenshot.rect_height - self.drag_point_radius),
            # Top side.
            (screenshot.x + screenshot.rect_width / 2 - self.drag_point_radius, screenshot.y - self.drag_point_radius),
            # Bottom side.
            (screenshot.x + screenshot.rect_width / 2 - self.drag_point_radius, screenshot.y + screenshot.rect_height - self.drag_point_radius),
            # Left side.
            (screenshot.x - self.drag_point_radius, screenshot.y + screenshot.rect_height / 2 - self.drag_point_radius),
            # Right side.
            (screenshot.x + screenshot.rect_width - self.drag_point_radius, screenshot.y + screenshot.rect_height / 2 - self.drag_point_radius))

    def get_position(self, event):
        '''
        Get drag position.
        @param event: the mouse event
        @return: one of DRAG POS Type Constants
        '''
        screenshot = self.screenshot
        # Get event position.
        (ex, ey) = self.get_event_coord(event)
        # Get drag point coords.
        pWidth = pHeight = self.drag_point_radius* 2
        ((tlX, tlY), (trX, trY), (blX, blY), (brX, brY), (tX, tY), (bX, bY), (lX, lY), (rX, rY)) = self.get_drag_point_coords()
        
        # Calculate drag position.
        if is_collide_rect((ex, ey), (tlX, tlY, pWidth, pHeight)):
            return DRAG_TOP_LEFT_CORNER
        elif is_collide_rect((ex, ey), (trX, trY, pWidth, pHeight)):
            return DRAG_TOP_RIGHT_CORNER
        elif is_collide_rect((ex, ey), (blX, blY, pWidth, pHeight)):
            return DRAG_BOTTOM_LEFT_CORNER
        elif is_collide_rect((ex, ey), (brX, brY, pWidth, pHeight)):
            return DRAG_BOTTOM_RIGHT_CORNER
        elif is_collide_rect((ex, ey), (tX, tY, pWidth, pHeight)) or is_collide_rect((ex, ey), (screenshot.x, screenshot.y, screenshot.rect_width, self.frame_border)):
            return DRAG_TOP_SIDE
        elif is_collide_rect((ex, ey), (bX, bY, pWidth, pHeight)) or is_collide_rect((ex, ey), (screenshot.x, screenshot.y + screenshot.rect_height, screenshot.rect_width, self.frame_border)):
            return DRAG_BOTTOM_SIDE
        elif is_collide_rect((ex, ey), (lX, lY, pWidth, pHeight)) or is_collide_rect((ex, ey), (screenshot.x, screenshot.y, self.frame_border, screenshot.rect_height)):
            return DRAG_LEFT_SIDE
        elif is_collide_rect((ex, ey), (rX, rY, pWidth, pHeight)) or is_collide_rect((ex, ey), (screenshot.x + screenshot.rect_width, screenshot.y, self.frame_border, screenshot.rect_height)):
            return DRAG_RIGHT_SIDE
        elif is_in_rect((ex, ey), (screenshot.x, screenshot.y, screenshot.rect_width, screenshot.rect_height)):
            return DRAG_INSIDE
        else:
            return DRAG_OUTSIDE
        



        
    def set_cursor(self, cursor_type):
        '''
        set cursor type
        @param cursor_type: one of cursor Type Constants in theme moudle
        '''
#         if cursor_type in theme_cursor:
#             set_cursor(self.window, theme_cursor[cursor_type])
#         else:
#             set_cursor(self.window, None)

    def _save_to_file(self):
        ''' Ctrl + s has been pressed'''
        self.save_to_file()

    def show(self):
        '''show root window'''
        self.window.show_all()
        self.window.window.raise_()

    def __move_area(self, x, y):
        screenshot = self.screenshot
        if screenshot.action == ACTION_WINDOW_SELECTED:
            new_x = min(max(screenshot.x + x, screenshot.monitor_x),
                screenshot.monitor_x + screenshot.width - screenshot.rect_width)
            new_y = min(max(screenshot.y + y, screenshot.monitor_y),
                screenshot.monitor_y + screenshot.height - screenshot.rect_height)
            if screenshot.x != new_x or screenshot.y != new_y:
                screenshot.x = new_x
                screenshot.y = new_y
                self.refresh()

    def move_area_up(self):
        self.__move_area(0, -1)

    def move_area_down(self):
        self.__move_area(0, 1)

    def move_area_left(self):
        self.__move_area(-1, 0)

    def move_area_right(self):
        self.__move_area(1, 0)

    def __extend_area(self, x, y):
        screenshot = self.screenshot
        if screenshot.action != ACTION_WINDOW_SELECTED:
            return
        is_changed = False
        if x > 0:       # Right
            new_width = min(
                screenshot.rect_width + 1,
                screenshot.monitor_x + screenshot.width - screenshot.x)
            if screenshot.rect_width != new_width:
                screenshot.rect_width = new_width
                is_changed = True
        elif x < 0:     # Left
            new_x = max(screenshot.x - 1, screenshot.monitor_x)
            if screenshot.x != new_x:
                screenshot.x = new_x
                screenshot.rect_width += 1
                is_changed = True
        if y > 0:       # Down
            new_height = min(
                screenshot.rect_height + 1,
                screenshot.monitor_y + screenshot.height - screenshot.y)
            if screenshot.rect_height != new_height:
                screenshot.rect_height = new_height
                is_changed = True
        elif y < 0:     # Up
            new_y = max(screenshot.y - 1, screenshot.monitor_y)
            if screenshot.y != new_y:
                screenshot.y = new_y
                screenshot.rect_height += 1
                is_changed = True
        if is_changed:
            self.refresh()

    def extend_area_up(self):
        self.__extend_area(0, -1)

    def extend_area_down(self):
        self.__extend_area(0, 1)

    def extend_area_left(self):
        self.__extend_area(-1, 0)

    def extend_area_right(self):
        self.__extend_area(1, 0)

    def _scroll_event(self, widget, event):
        screenshot = self.screenshot
        if screenshot.action != ACTION_WINDOW_SELECTED:
            return
        if event.state & gtk.gdk.CONTROL_MASK == 0:
            return
        is_changed = False
        if event.direction == gtk.gdk.SCROLL_UP:        # zoom in
            new_x = max(screenshot.x - 1, screenshot.monitor_x)
            new_y = max(screenshot.y - 1, screenshot.monitor_y)
            if screenshot.x != new_x or screenshot.y != new_y:
                screenshot.x = new_x
                screenshot.y = new_y
                is_changed = True
            new_width = min(
                screenshot.rect_width + 2,
                screenshot.monitor_x + screenshot.width - screenshot.x)
            new_height = min(
                screenshot.rect_height + 2,
                screenshot.monitor_y + screenshot.height - screenshot.y)
            if screenshot.rect_width != new_width or screenshot.rect_height != new_height:
                screenshot.rect_width = new_width
                screenshot.rect_height = new_height
                is_changed = True
        if event.direction == gtk.gdk.SCROLL_DOWN:      # zoom out
            new_x = min(screenshot.x + 1, screenshot.x + screenshot.rect_width - 2)
            new_y = min(screenshot.y + 1, screenshot.y + screenshot.rect_height - 2)
            if screenshot.x != new_x or screenshot.y != new_y:
                screenshot.x = new_x
                screenshot.y = new_y
                is_changed = True
            new_width = max(screenshot.rect_width - 2, 2)
            new_height = max(screenshot.rect_height - 2, 2)
            if screenshot.rect_width != new_width or screenshot.rect_height != new_height:
                screenshot.rect_width = new_width
                screenshot.rect_height = new_height
                is_changed = True
        if is_changed:
            self.refresh()

