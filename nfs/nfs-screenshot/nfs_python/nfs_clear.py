#! /usr/bin/env python
# -*- coding: utf-8 -*-
#Copyright (c) 2016-2018 CPU and Fundamental Software Research Center,CAS
#This software is published by the license of CPU-OS License，you can use and 
#distibuted this software under this License.See CPU-OS Liense for more detail.
#You should have receive a copy of CPU-OS License.If not,please contact us 
# by email <support_os@cpu-os.ac.cn> 
import os
import os.path
import time
import shutil

path = os.path.expanduser('~')+"/图片/.nfs"


b = os.path.exists(path)
if(b == 0):
	os.mkdir(path)

systemTime = time.time()
lastModifyPath = ''
lastModifyTime = 0
if os.path.isdir(path):
	lencount = len(os.listdir(path))
	if ( lencount > 0 ):
		#这里需要遍历文件，拿到所有文件中最后修改的文件
		for i in os.listdir(path):
   			 if os.path.isfile(os.path.join(path,i)):
				#文件存在的话，这里获取文件的最后修改时间
				statinfo = os.stat(os.path.join(path,i))	        			
				#print statinfo.st_mtime
				#print time.localtime(statinfo.st_mtime)
				if ( (systemTime - statinfo.st_mtime) <= 1000*3 and statinfo.st_mtime >= lastModifyTime ):
					lastModifyTime = statinfo.st_mtime								
					lastModifyPath = os.path.join(path,i)
		#print lastModifyPath
		os.remove(lastModifyPath)
