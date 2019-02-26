import pandas as pd
data = pd.read_csv('D:\\lab-env\\rssitools\\data\\rssidata2019-02-03-12-27-54.csv')
data = data.iloc[:,1:]

###2维散点图
import matplotlib.pyplot as plt

k=[
'Sepal.Length',
'Sepal.Width',
'Petal.Length',
'Petal.Width',]
for i in k:
    for m in k:
        if i != m:
            plt.figure(figsize=(10,10))
            result =data.Species.unique()
            plt.scatter(data.loc[data.Species == result[2], i], data.loc[data.Species == result[2],m], s = 35, marker='*', c ='g')
            plt.scatter(data.loc[data.Species == result[1], i], data.loc[data.Species == result[1],m], s = 35, marker='+', c ='r')
            plt.scatter(data.loc[data.Species == result[0], i], data.loc[data.Species == result[0],m], s = 35, marker='o',c = 'y')
            # 添加轴标签和标题
            plt.title( '')
            plt.xlabel(i)
            plt.ylabel(m)
            # 去除图边框的顶部刻度和右边刻度
            #lt.tick_params(top = 'off', right = 'off')
            # 添加图例plt.legend(loc = 'upper left')
            plt.show()

####三维散点图
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

k=[
'Sepal.Length',
'Sepal.Width',
'Petal.Length',
'Petal.Width',]
for i in k:
    for m in k:
        for z in k:
            if i != m and m!=z and 1!=z:
                plt.figure(figsize=(10,10))
                result = data.Species.unique()
                ax = plt.subplot(111, projection='3d')  # 创建一个三维的绘图工程
                ax.scatter(data.loc[data.Species == result[2], i], data.loc[data.Species == result[2], m], data.loc[data.Species == result[2], z], c='g',marker='*')  # 绘制数据点
                ax.scatter(data.loc[data.Species == result[1], i], data.loc[data.Species == result[1], m], data.loc[data.Species == result[1], z], c='r',marker='+')  # 绘制数据点
                ax.scatter(data.loc[data.Species == result[0], i], data.loc[data.Species == result[0], m], data.loc[data.Species == result[0], z], c='y',marker='o')  # 绘制数据点
                ax.set_zlabel(z)  # 坐标轴
                ax.set_ylabel(m)
                ax.set_xlabel(i)
                plt.show()