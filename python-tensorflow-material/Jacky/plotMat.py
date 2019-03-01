import  matplotlib.pyplot as plt
import pandas as pd
from pandas import Series, DataFrame
import random
import numpy as np
import matplotlib as mpl
import datetime#这个包很关键

# ts = Series(np.random.rand(1000), index=pd.date_range('1/1/2000', periods=1000))
# ts = ts.cumsum()
# plt.plot(ts)
# plt.show()



#  设定开始和结束时间
start=datetime.datetime(2013,1,1)
stop=datetime.datetime(2013,12,31)
delta=datetime.timedelta(1) #设定日期的间隔
dates=mpl.dates.drange(start,stop,delta) # 返回浮点型的日期序列，这个是生成时间序列，同理如果是将序列转成日期呢？
values=np.random.rand(len(dates))
#存在两个问题，一个是坐标轴没有按照日期的形式去标注，另一个是刻度的数量和位置也不合适
fig=plt.figure(figsize=(24,12))#调整画图空间的大小
plt.plot(dates,values,linestyle='-',marker='*',c='r',alpha=0.5)#作图
ax=plt.gca()
date_format=mpl.dates.DateFormatter('%Y-%m-%d')#设定显示的格式形式
ax.xaxis.set_major_formatter(date_format)#设定x轴主要格式
ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(30))#设定坐标轴的显示的刻度间隔
fig.autofmt_xdate()#防止x轴上的数据重叠，自动调整。

plt.show()