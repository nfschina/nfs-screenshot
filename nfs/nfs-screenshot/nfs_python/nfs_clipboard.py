#coding=utf-8
import gtk
import sys
#import io
#img=io.imread('./3.png')
#import cv2  
#img = cv2.imread('./3.png')  
from urllib import unquote



def copy_gtk(image):
        global cb
        cb = gtk.Clipboard()
        pixbuf = gtk.gdk.pixbuf_new_from_file(unquote(image).strip())
        cb.set_image(pixbuf)
        cb.store()

def paste_gtk():
        clipboardContents = gtk.Clipboard().wait_for_text()  # for python 2, returns None if the clipboard is blank.
        if clipboardContents is None:
            return ''
        else:
            return clipboardContents

   # return copy_gtk, paste_gtk 


#init_gtk_clipboard()
copy_gtk(sys.argv[1])
#copy_gtk('/home/nfs/图片/.nfs/nfs_20190403161914.png')

