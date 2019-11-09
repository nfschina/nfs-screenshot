#Copyright (c) 2016-2018 CPU and Fundamental Software Research Center,CAS
#This software is published by the license of CPU-OS Licensu,you can use and 
#distibuted this software under this License.See CPU-OS Liense for more detail.
#You should have receive a copy of CPU-OS License.If not,please contact us 
# by email <support_os@cpu-os.ac.cn> 
import virtkey
import time

v = virtkey.virtkey()
v.press_keysym(65507) 
v.press_keysym(65513) 
v.press_unicode(ord('w')) 
v.release_unicode(ord('w'))
v.release_keysym(65513) 
v.release_keysym(65507)
#time.sleep(5)
#v.press_keysym(65421)
#v.release_keysym(65421)
