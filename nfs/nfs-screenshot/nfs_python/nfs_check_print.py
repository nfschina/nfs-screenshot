#! /usr/bin/env python
# -*- coding: utf-8 -*-
#Copyright (c) 2016-2018 CPU and Fundamental Software Research Center,CAS
#This software is published by the license of CPU-OS License,you can use and 
#distibuted this software under this License.See CPU-OS Liense for more detail.
#You should have receive a copy of CPU-OS License.If not,please contact us 
# by email <support_os@cpu-os.ac.cn> 
import os
import os.path
import time
import datetime as dt
import shutil     

path = os.path.expanduser('~')+"/图片/.nfsprint"
#shutil.rmtree(path)
#由于每次print键都会清空文件夹，所以这里只要拿到文件夹下唯一的内容显示即可
systemTime = time.time()
lastModifyPath = ''
if os.path.isdir(path):
	lencount = len(os.listdir(path))
	if ( lencount > 0 ):
		#这里需要遍历文件，拿到所有文件中最后修改的文件
		for i in os.listdir(path):
   			 if os.path.isfile(os.path.join(path,i)):
				#文件存在的话，这里获取文件的最后修改时间
				statinfo = os.stat(os.path.join(path,i))	        			
				
				timeArray = time.localtime(statinfo.st_mtime)
				otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
				time1 = dt.datetime.strptime(otherStyleTime,'%Y-%m-%d %H:%M:%S')
				#print (dt.datetime.now() - time1).seconds
				if ( (dt.datetime.now() - time1).seconds <= 5):								
					lastModifyPath = os.path.join(path,i)
		print lastModifyPath
				
	else:
		print ""
else:
	print ""
