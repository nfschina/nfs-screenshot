#!/usr/bin/python
#-*- coding:utf-8 -*-
#Copyright (c) 2016-2018 CPU and Fundamental Software Research Center,CAS
#This software is published by the license of CPU-OS License，you can use and 
#distibuted this software under this License.See CPU-OS Liense for more detail.
#You should have receive a copy of CPU-OS License.If not,please contact us 
# by email <support_os@cpu-os.ac.cn>  
#模块描述：
#   主文件
#
#作者: liangjian
#日期：2014-08-20


from nfs_constant import *
from nfs_window import *
from nfs_widget import RootWindow
from nfs_nls import _
import pygtk
import cairo

pygtk.require('2.0')
import gtk
import Image


class Screenshot(object):
    ''' Main Screenshot. '''
    def __init__(self):
        '''Init Main screenshot.'''
        # Init.
        self.action = ACTION_WINDOW_INIT         # current action status
        self.screenshot_window_info = get_screenshot_window_info()
        self.monitor_x, self.monitor_y, self.width, self.height = get_current_monitor_info()
        self.x = self.y = self.rect_width = self.rect_height = 0

        self.save_op_index = SAVE_OPERATION_AS   # current operation when the save button clicked

        self.drag_position = None
        self.last_drag_position = None
        self.dragStartX = self.dragStartY = self.dragStartOffsetX = self.dragStartOffsetY = 0
        self.textDragOffsetX = self.textDragOffsetY = 0

        self.drag_flag = False              # a flag if the selected area can be dragged
        self.window_flag = True             # a flag if has not selected area or window

        self.saveFiletype = 'png'
        self.saveFilename = ''

        # Init action list.
        self.current_action = None          # current drawing action
        self.action_list = []               # a list of actions have created
        self.current_text_action = None     # current drawing text action
        self.text_action_list = []          # a list of text actions have created
        self.text_action_info = {}          # the created text actions' info

        # Get desktop background.
        # a gtk.gdk.Pixbuf of the desktop_background
        self.desktop_background = self.get_desktop_snapshot()
        # a string containing the pixel data of the pixbuf
        self.desktop_background_pixels= self.desktop_background.get_pixels()
        # the number of the pixbuf channels.
        self.desktop_background_n_channels = self.desktop_background.get_n_channels()
        # the number of bytes between rows.
        self.desktop_background_rowstride = self.desktop_background.get_rowstride()

        # Init window.
        self.window = RootWindow(self)

        # Show.
        self.window.show()
        self.window.set_cursor(ACTION_WINDOW_INIT)
#         nfs_dss.hide()
        
        

    def set_action_type(self, action_type):
        '''
        Set action type
        @param action_type: one of ACTION Type Constants
        '''
        self.action = action_type
        self.current_action = None

    def save_snapshot(self, filename=None, filetype='png', clip_flag=True):
        '''
        Save snapshot.
        @param filename: the filename to save, a string type
        @param filetype: the filetype to save, a string type. Default is 'png'
        @param clip_flag: a flag if copy the snapshot to clipboard. Default is False
        '''
        failed_flag = False
        tipContent = ""
#         parent_dir = get_parent_dir(__file__, 1)
        # Save snapshot.
        if self.rect_width == 0 or self.rect_height == 0:
            tipContent = _("The width or height of selected area cannot be 0")
            failed_flag = True
        else:
            self.window.finish_flag = True
            surface = self.make_pic_file(
                self.desktop_background.subpixbuf(*self.get_rectangel_in_monitor()))
            # Save to file
            
            if filename:
                
                try:
                    surface.write_to_png(filename)
#                     SCROT_BUS.emit_finish(1, filename)
                    
                    '''根据文件后缀重新设置文件类型'''
                    str = filename.split('.')
                    imagetype =  str[len(str)-1]
                
                    im = Image.open(filename)
                    
                    if imagetype == 'jpg' or imagetype == 'jpeg':
                        im.save(filename,"jpeg")
                    elif imagetype == 'bmp' or imagetype == 'gif':
                        im.save(filename, imagetype)
                    elif imagetype == 'png':
                        im.save(filename, imagetype)
                    else:
                        im.save(filename.replace(imagetype, 'png'), 'png')
                        os.remove(filename)
                    
                    print filename
                    # 拷贝到剪切板
                    if clip_flag:
                        pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
                        clipboard = gtk.Clipboard(selection="CLIPBOARD")
                        clipboard.set_image(pixbuf)
                        clipboard.store()


                except Exception, e:
                    tipContent = "%s:%s" % (_("Failed to save the picture"), str(e))
            # 保存图片到剪切板
            else:
                import StringIO
                fp = StringIO.StringIO()
                surface.write_to_png(fp)
                contents = fp.getvalue()
                fp.close()
                loader = gtk.gdk.PixbufLoader("png")
                loader.write(contents, len(contents))
                pixbuf = loader.get_pixbuf()
                loader.close()

                clipboard = gtk.Clipboard(selection="CLIPBOARD")
                if pixbuf:
                    clipboard.set_image(pixbuf)
                clipboard.store()
                tipContent += _("Picture has been saved to clipboard")


        # Exit
        self.window.destroy_all()
            
            

    def make_pic_file(self, pixbuf):
        '''
        use cairo to make a picture file
        @param pixbuf: gtk.gdk.Pixbuf
        @return: a cairo.ImageSurface object
        '''
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, pixbuf.get_width(), pixbuf.get_height())
        cr = cairo.Context(surface)
        gdkcr = gtk.gdk.CairoContext(cr)
        gdkcr.set_source_pixbuf(pixbuf, 0, 0)
        gdkcr.paint()
 
        for action in self.action_list:
            if action is not None:
                action.start_x -= self.x - self.monitor_x
                action.start_y -= self.y - self.monitor_y
                if not isinstance(action, (TextAction)):
                    action.end_x -= self.x - self.monitor_x
                    action.end_y -= self.y - self.monitor_y
                if isinstance(action, (LineAction)):
                    for track in action.track:
                        track[0] -= self.x - self.monitor_x
                        track[1] -= self.y - self.monitor_y
                action.expose(cr)
 
        # Draw Text Action list.
        for each in self.text_action_list:
            if each is not None:
                each.expose(cr)
        return surface

    def save_to_tmp_file(self):
        if self.rect_width > 0 and self.rect_height > 0:
            from tempfile import mkstemp
            import os
            tmp = mkstemp(".tmp", "screenshot")
            os.close(tmp[0])
            filename = tmp[1]
            self.window.finish_flag = True
            surface = self.make_pic_file(
                self.desktop_background.subpixbuf(*self.get_rectangel_in_monitor()))
            surface.write_to_png(filename)
            SCROT_BUS.emit_finish(1, filename)
        gtk.main_quit()
        return filename

    def parse_barcode(self):
        filename = self.save_to_tmp_file()
        import os
        from nfs_decode_zbar import decode_zbar
        os.remove(filename)

    def get_desktop_snapshot(self):
        '''
        Get desktop snapshot.
        @return: a gtk.gdk.Pixbuf object
        '''
        return get_screenshot_pixbuf()

    def undo(self, widget=None):
        '''
        Undo the last action.
        '''

        if self.current_text_action:
            self.current_text_action = None

        if self.action_list:        # undo the previous action
            tempAction = self.action_list.pop()
            if tempAction.get_action_type() == ACTION_TEXT:
                self.text_action_list.pop()
                if tempAction in self.text_action_info:
                    del self.text_action_info[tempAction]
        else:       # back to select area
            self.window.set_cursor(ACTION_WINDOW_INIT)
            self.window.magnifier = None
            self.action = ACTION_WINDOW_INIT
            self.x = self.y = self.rect_width = self.rect_height = 0
            self.window_flag = True
            self.drag_flag = False

        self.window.refresh()

    def get_rectangel(self):
        '''
        get select rectangle
        @return: a tuple contain the selected area coordinate.
        '''
        return (int(self.x), int(self.y), int(self.rect_width), int(self.rect_height))

    def get_rectangel_in_monitor(self):
        '''
        get select rectangle in the monitor
        @return: a tuple contain the selected area coordinate in this monitor.
        '''
        return (int(self.x-self.monitor_x), int(self.y-self.monitor_y),
                int(self.rect_width), int(self.rect_height))

    def get_monitor_info(self):
        '''
        get monitor info
        @return: a tuple contain this monitor coordinate.
        '''
        return (self.monitor_x, self.monitor_y, self.width, self.height)


def main():
    ''' main function '''
    Screenshot()
    gtk.main()

if __name__ == '__main__':
    main()
