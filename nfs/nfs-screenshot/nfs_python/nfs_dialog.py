#!/usr/bin/python
#-*- coding:utf-8 -*-
#Copyright (c) 2016-2018 CPU and Fundamental Software Research Center,CAS
#This software is published by the license of CPU-OS License，you can use and 
#distibuted this software under this License.See CPU-OS Liense for more detail.
#You should have receive a copy of CPU-OS License.If not,please contact us 
# by email <support_os@cpu-os.ac.cn> 
import gtk
import Image
import base64
import time
import sys
import os
import getpass
import nfs_common
import gettext
import urllib
import re

def change_filetype(self, dialog, filename):
    
    filename = dialog.get_filename()
    #print dialog.get_filename()
    #print filename		    
    inx = filename.rfind("/")
    filename = filename[inx+1:]

    #符号所在字符串的index
    pos = filename.rfind(".")
    
    if self.get_active() == 0:
        filename = filename[:pos] + ".png"
    elif self.get_active() == 1:
        filename = filename[:pos] + ".jpg"
    elif self.get_active() == 2:
        filename = filename[:pos] + ".gif"
    else:
        filename = filename[:pos] + ".png"

    dialog.set_current_name(filename)   
    
#user_path=os.path.expanduser("~")+'/.locale/'
#gettext.bindtextdomain('nfs_dialog', user_path)
gettext.textdomain('nfs_dialog')
_ = gettext.gettext

def save_pic(file_path):
    #user_path=os.path.expanduser("~")+'/.locale/'
    #gettext.bindtextdomain('nfs_dialog', user_path)
    #gettext.textdomain('nfs_dialog')
    #_ = gettext.gettext 
    dialog = gtk.FileChooserDialog(
                _("Save As"),
                None,
                gtk.FILE_CHOOSER_ACTION_SAVE,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                 gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))
    dialog.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
    dialog.set_default_response(gtk.RESPONSE_ACCEPT)
    dialog.set_position(gtk.WIN_POS_MOUSE)
    dialog.set_local_only(True)
#    dialog.set_keep_above(True)

    filename = "%s%s.%s" % ('NFS', time.strftime("%Y%m%d%H%M%S", time.localtime()), "png")
    dialog.set_current_name(filename)
    dialog.set_current_folder(nfs_common.get_pictures_dir())
    
    '''创建一个额外的选择类型的组件'''
    extra_hbox = gtk.HBox()
    label_save_as_type = gtk.Label(_("Image Format:"))
    combobox_save_as_type = gtk.combo_box_new_text()
    combobox_save_as_type.append_text("PNG(*.png)")
    combobox_save_as_type.append_text("JPEG(*.jpg,*.jpeg)")
    combobox_save_as_type.append_text("GIF(*.gif)")
    combobox_save_as_type.set_active(0)
    '''给类型选择添加事件'''
    
    
    extra_hbox.pack_start(label_save_as_type, False, False, 5)
    extra_hbox.pack_start(combobox_save_as_type, False, False, 5)
    
    align_save_as_type = gtk.Alignment(1, 0, 0, 0)
    align_save_as_type.add(extra_hbox)
    align_save_as_type.show_all()
    
    dialog.set_extra_widget(align_save_as_type)
    
    
    combobox_save_as_type.connect("changed", change_filetype, dialog, filename)
#     '''base64转为图片格式'''
#     if leniystr != '':
#         imgData = base64.b64decode(leniystr)
#         leniyimg = open('imgout','wb')
#         leniyimg.write(imgData)
#         leniyimg.close()
    handle_file_dialog(dialog,file_path)
  
def handle_file_dialog(dialog,file_path):
    response = dialog.run()
    if response == gtk.RESPONSE_ACCEPT:
        cansave = False
        filename = dialog.get_filename()
        if os.path.exists(filename) == True:
            #dialog2 = DialogSaveFile(self,filename)
            #dialog2 = gtk.MessageDialog(None,0,gtk.MESSAGE_QUESTION,gtk.BUTTONS_OK_CANCEL,None)
            #dialog2 = DialogSaveFile(None, dialog.get_filename()) 
            dialog2 = gtk.MessageDialog(None, gtk.DIALOG_MODAL |
                                     gtk.DIALOG_DESTROY_WITH_PARENT,
                                    gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO, _("This file already exists. Do you want to replace it?"))

            response2 = dialog2.run()
            if response2==gtk.RESPONSE_YES:
                cansave = True
                dialog2.destroy()
            else:
                dialog2.destroy()
                handle_file_dialog(dialog,file_path)
        else:
            cansave = True
        if cansave == True:
            _save_to_file_cb(filename,file_path)
            dialog.destroy()
        else:
            pass
    else:
        print ''
        dialog.destroy()



def _save_to_file_cb(filename, file_path):

    str = filename.split('.')
    imagetype =  str[len(str)-1]
    im = Image.open(file_path)
    if imagetype == 'jpg' or imagetype == 'jpeg':
        im.save(filename,"jpeg")
    elif imagetype == 'bmp' or imagetype == 'gif':
        im.save(filename, imagetype)
    elif imagetype == 'png':
        im.save(filename, imagetype)
    print filename
            
    
        



if __name__ == '__main__':
    
    if len(sys.argv) >= 2:
        file_path = sys.argv[1]
        if file_path != '':
            save_pic(file_path)




