# -*- coding=utf-8 -*-
import numpy as np
import csv    #需要加载numpy和csv两个包
csv_file=open('D:\\新建文件夹\\2018-12-26\\input_2018-12-26 11-07-41_zmt_sitechuang_tang.csv')   	#打开文件
csv_reader_lines = csv.reader(csv_file)    							    #用csv.reader读文件
date_PyList=[]
for one_line in csv_reader_lines:
	date_PyList.append(one_line)
	print(one_line)
	date_ndarray = np.array(date_PyList)    								#将python列表转化为ndarray
print (date_ndarray.dtype())