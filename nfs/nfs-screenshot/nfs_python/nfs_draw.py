#!/usr/bin/python
#-*- coding:utf-8 -*-
#Copyright (c) 2016-2018 CPU and Fundamental Software Research Center, CAS
#Based on code from src/draw.py in deepin-screenshot-2.0
#Copyright (C) 2011 Deepin, Inc.
#               2011 Wang Yong
#
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
#This software is published by the license of CPU-OS License,you can use and 
#distibuted this software under this License.See CPU-OS Liense for more detail.
#You should have receive a copy of CPU-OS License.If not,please contact us 
#by email <support_os@cpu-os.ac.cn>  
#模块描述：
#
#
#作者: liangjian
#日期：2014-08-20

from nfs_common import  *
from math import pi
from nfs_constant import DEFAULT_FONT
import cairo
import gtk
import math
import pango
import pangocairo
from pango import ALIGN_CENTER
pygtk.require('2.0') # 设置pygtk的版本




def render_text(cr, markup, 
                x, y, w, h, 
                text_size=2, 
                text_color="#000000", 
                text_font=DEFAULT_FONT, 
                alignment=pango.ALIGN_LEFT,
                wrap_width=None, 
                vertical_alignment=2,
                clip_line_count=None,
                ellipsize=pango.ELLIPSIZE_END,
                ):

    cr.set_source_rgb(1, 1, 1)
    
    # Create pangocairo context.
    context = pangocairo.CairoContext(cr)
    
    # Set layout.
    layout = context.create_layout()
    layout.set_font_description(pango.FontDescription("%s %s" % (text_font, text_size)))
    layout.set_markup(markup)
    layout.set_alignment(alignment)
    if wrap_width == None:
        layout.set_single_paragraph_mode(True)
        layout.set_width(w * pango.SCALE)
        layout.set_ellipsize(ellipsize)
    else:
        layout.set_width(wrap_width * pango.SCALE)
        layout.set_wrap(pango.WRAP_WORD)
        
    (text_width, text_height) = layout.get_pixel_size()
            
    # Set render y coordinate.
    if vertical_alignment == 1:
        render_y = y
    elif vertical_alignment == 2:
        render_y = y + max(0, (h - text_height) / 2)
    else:
        render_y = y + max(0, h - text_height)
        
    # Clip area.
    if clip_line_count:
        line_count = layout.get_line_count()
        if line_count > 0:
            line_height = text_height / line_count
            cr.rectangle(x, render_y, text_width, line_height * clip_line_count)
            cr.clip()
        
    # Draw text.
    cr.move_to(x, render_y)
    context.update_layout(layout)
    context.show_layout(layout)
        


def drawPixbuf(cr, pixbuf, x=0, y=0):
    '''
    Draw pixbuf.
    @param cr: a gtk.gdk.CairoContext
    @param pixbuf: a gtk.gdk.Pixbuf
    @param x: the X coordinate of the location to place the upper left corner of pixbuf.
    @param y: the Y coordinate of the location to place the upper left corner of pixbuf.
    '''
    if pixbuf != None:
        cr.set_source_pixbuf(pixbuf, x, y)
        cr.paint()

def colorHexToCairo(color):
    """
    Convert a html (hex) RGB value to cairo color.

    @type color: html color string
    @param color: The color to convert.
    @return: A color in cairo format.
    """
    if color[0] == '#':
        color = color[1:]
    (r, g, b) = (int(color[:2], 16),
                    int(color[2:4], 16),
                    int(color[4:], 16))
    return colorRGBToCairo((r, g, b))

def colorRGBToCairo(color):
    """
    Convert a 8 bit RGB value to cairo color.

    @type color: a triple of integers between 0 and 255
    @param color: The color to convert.
    @return: A color in cairo format.
    """
    return (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)


def draw_ellipse(cr, ex, ey, ew, eh, color, size, fill):
    '''
    Draw ellipse
    @param cr: a gtk.gdk.CairoContext
    @param ex: the X coordinate of the ellipse's center
    @param ey: the Y coordinate of the ellipse's center
    @param ew: the ellipse's width, a float num
    @param eh: the ellipse's height, a float num
    @param color: the ellipse's color, an hex string
    @param size: the ellipse's border width
    @param fill: a flag that the ellipse is stroke or fill.
    '''
    cr.new_path()
    cr.save()
    cr.translate(ex, ey)
    cr.scale(ew / 2.0, eh / 2.0)
    cr.arc(0.0, 0.0, 1.0, 0.0, 2 * pi)
    cr.restore()
    cr.set_source_rgb(*colorHexToCairo(color))
    cr.set_line_width(size)
    if fill:
        cr.fill()
    else:
        cr.stroke()



def updateShape(widget, allocation, radius):
    '''Update shape.'''
    if allocation.width > 0 and allocation.height > 0:
        # Init.
        w, h = allocation.width, allocation.height
        bitmap = gtk.gdk.Pixmap(None, w, h, 1)
        cr = bitmap.cairo_create()

        # Clear the bitmap
        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()

        # Draw our shape into the bitmap using cairo
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        draw_round_rectangle(cr, 0, 0, w, h, radius)
        cr.fill()

        widget.shape_combine_mask(bitmap, 0, 0)

def draw_round_rectangle(cr, x, y, width, height, r):
    '''
    Draw round rectangle.
    @param cr: a gtk.gdk.CairoContext
    @param x: the x coordinate of the rectangle left-top point
    @param y: the y coordinate of the rectangle left-top point
    @param width: the rectangle's width
    @param height: the rectangle's height
    @param r: Radious of rectangle corner.
    '''
    cr.move_to(x + r, y)
    cr.line_to(x + width - r, y)

    cr.move_to(x + width, y + r)
    cr.line_to(x + width, y + height - r)

    cr.move_to(x + width - r, y + height)
    cr.line_to(x + r, y + height)

    cr.move_to(x, y + height - r)
    cr.line_to(x, y + r)

    cr.arc(x + r, y + r, r, pi, 3 * pi / 2.0)
    cr.arc(x + width - r, y + r, r, 3 * pi / 2, 2 * pi)
    cr.arc(x + width - r, y + height - r, r, 0, pi / 2)
    cr.arc(x + r, y + height - r, r, pi / 2, pi)

def exposeBackground(widget, event, dPixbuf):
    '''Expose background.'''
    cr = widget.window.cairo_create()
    rect = widget.allocation

    drawPixbuf(cr, dPixbuf.getPixbuf().scale_simple(rect.width, rect.height, gtk.gdk.INTERP_BILINEAR), rect.x, rect.y)

    if widget.get_child() != None:
        widget.propagate_expose(widget.get_child(), event)

    return True

def draw_round_text_rectangle(cr, x, y, width, height, r, Text, alpha=0.8):
    '''
    draw Round Text Rectangle
    @param cr: a gtk.gdk.CairoContext
    @param x: the x coordinate of the rectangle left-top point
    @param y: the y coordinate of the rectangle left-top point
    @param width: the rectangle's width
    @param height: the rectangle's height
    @param r: Radious of rectangle corner.
    @param Text: the text to draw, a string type
    @param alpha: Alpha value to render pixbuf, float value between 0 and 1.0
    '''
    cr.set_source_rgba(0.14, 0.13, 0.15, alpha)
    cr.move_to(x+r, y)
    cr.line_to(x+width-r,y)

    cr.move_to(x+width, y+r)
    cr.line_to(x+width, y+height - r)

    cr.move_to(x+width-r,y+height)
    cr.line_to(x+r, y+height)

    cr.move_to(x, y+height-r)
    cr.line_to(x, y+r)
    cr.arc(x+r, y+r, r, pi, 3*pi / 2)
    cr.arc(x+width-r,y+r,r, 3*pi / 2, 2*pi)
    cr.arc(x+width-r, y+height-r, r, 2*pi, pi / 2)
    cr.arc(x+r, y+height-r, r, pi / 2, pi)
    cr.fill()

    #draw_font(cr, Text, 14.0, "#FFFFFF", x + width / 12.0, y + height / 1.5)
    render_text(cr, Text, x, y, width, height, 9, "#FFFFFF", DEFAULT_FONT, ALIGN_CENTER)
    
    
def draw_font(cr, content, fontSize, fontColor, x, y):
    '''
    Draw font.
    @param cr: a gtk.gdk.CairoContext
    @param content: the text to draw, a string type
    @param fontSize: the text size, an int type
    @param fontColor: the text color, a hex string
    @param x: the x coordinate of source point
    @param y: the y coordinate of source point
    '''
#     if DEFAULT_FONT in get_font_families():
#         cr.select_font_face(DEFAULT_FONT,
#                             cairo.FONT_SLANT_NORMAL,
#                             cairo.FONT_WEIGHT_NORMAL)
    cr.set_source_rgb(*colorHexToCairo(fontColor))
    cr.set_font_size(fontSize)
    cr.move_to(x, y)
    cr.show_text(content)


