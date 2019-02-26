from socket import *
import sys
import signal
import asyncio

import numpy as np
import matplotlib.pyplot as plt

port = 9092  # 接口必须一致
# port = 9092  # 接口必须一致
addr = ('', port)
udpServer = socket(AF_INET, SOCK_DGRAM)
udpServer.bind(addr)  # 开始监听

bufsize = 102400
winSize = 2000
timelags = []  # 时间间隔
last_timest = 0

loop = asyncio.get_event_loop()

global total_fig
global init
init = 0

# 信号量通知 可退出


def quit(signum, frame):
    print('quit signal!!!')
    sys.exit()


def realtime_ploting(data):
    global total_fig
    global init

    # init
    if 0 == init:
        total_fig = plt.figure('CSI liveview', figsize=(12, 10))
        plt.ion()

    # body
    transsub = total_fig.add_subplot(1, 1, 1)
    transsub.clear()
    transsub.plot(data, linewidth=1, linestyle='--')
    transsub.set_ylim((0,10))
    # transsub.grid(True)
    transsub.set_ylabel('time lag (ms)')
    # transsub.hold(False)

    plt.pause(0.01)

    # end
    if 0 == init:
        init = 1


async def collectTimeSt(timestamp):
    global timelags, winSize, last_timest
    if last_timest == 0:
        last_timest = timestamp
        return

    timelag = timestamp - last_timest
    last_timest = timestamp
    print("timelag:", timelag)
    l = len(timelags)
    # print("winSize:",l)
    timelags.append(timelag/1000)
    if l >= winSize:
        realtime_ploting(timelags)
        timelags = timelags[10:winSize-1]


print('waiting to connection...（9092）')
signal.signal(signal.SIGINT, quit)
signal.signal(signal.SIGTERM, quit)

while 1:
    data, addr = udpServer.recvfrom(bufsize)  # 接收数据和返回地址
    date = int(str(data, "utf-8"))
    print(date)
    loop.run_until_complete(collectTimeSt(date))

udpServer.close()
loop.close()
