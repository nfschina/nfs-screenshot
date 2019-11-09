#! /usr/bin/env python
# -*- coding: utf-8 -*-
#Copyright (c) 2016-2018 CPU and Fundamental Software Research Center,CAS
#This software is published by the license of CPU-OS License，you can use and 
#distibuted this software under this License.See CPU-OS Liense for more detail.
#You should have receive a copy of CPU-OS License.If not,please contact us 
# by email <support_os@cpu-os.ac.cn> 
import os
import os.path
import shutil     

path = os.path.expanduser('~')+"/图片/.nfsprint"
if os.path.exists(path):
	shutil.rmtree(path);

os.mkdir(path)

