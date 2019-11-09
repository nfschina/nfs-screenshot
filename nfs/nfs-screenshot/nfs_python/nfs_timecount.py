#!/usr/bin/python
#-*- coding:utf-8 -*-
#Copyright (c) 2016-2018 CPU and Fundamental Software Research Center, CAS
#This software is published by the license of CPU-OS License，you can use and 
#distibuted this software under this License.See CPU-OS Liense for more detail.
#You should have receive a copy of CPU-OS License.If not,please contact us 
# by email <support_os@cpu-os.ac.cn> 
#
# zhuyun
#
# Countdown using Tkinter 
from Tkinter import *
import time



        
if __name__ == '__main__':
    
    
    num = 0;
    if len(sys.argv) > 1:
        num = int(sys.argv[1])
    
    root = Tk()
    root.overrideredirect(True)
    root.geometry("300x200-10-50")
    
    lbl1 = Label()
    lbl1.pack(fill=BOTH, expand=1)
    
    
    '''启动计时倒数'''
    lbl1.config(bg='#DCDCDC',fg='#292421')
    lbl1.config(height=3, font=('times', 15, 'bold'))
    for k in range(num, 0, -1):
        lbl1["text"] = str(k) + "秒后开始截图"
        root.update()
        time.sleep(1)
    lbl1.config(bg='red')
    lbl1.config(fg='white')
    lbl1["text"] = "Time up!"
    
    print 'time up'
    
    root.destroy()
    
    root.mainloop()
