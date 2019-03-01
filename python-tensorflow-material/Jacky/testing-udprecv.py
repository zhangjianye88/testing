
from socket import *
import time, datetime
import numpy as np
import base64
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
from mpl_toolkits.mplot3d import Axes3D
import sys

global streamNr
streamNr = 1

def bit_convert(data, maxbit):
    if (data & (1 << (maxbit -1))):
        data -= (1 << maxbit)
    return data



port = 9092  # 接口必须一致

addr = ('',port)

udpServer = socket(AF_INET, SOCK_DGRAM)
udpServer.bind(addr)  # 开始监听

bufsize = 100000

# count = 0

# 输入毫秒级的时间，转出正常格式的时间
def timeStamp(timeNum):
    us = timeNum[-3:]
    timeStamp = float(int(timeNum)/1000)
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    print(otherStyleTime+'.'+us)


def read_from_stream(stream):
    global streamNr

    cur = 0
    csi_matrix = {}

    # length = len(stream)
    # print('%d stream length is: %d\n' %(streamNr,length))
    # streamNr += 1

    # some embedded system use big endian. for 16/32/64 system this should be all fine
    endian_format = 'ieee-be'

    timestamp = np.frombuffer(stream, np.uint64, 1, cur)
    if endian_format != 'ieee-le':
        timestamp.dtype = '>u8'
    csi_matrix['timestamp'] = timestamp
    cur = cur + 8
    # print('timestamp is %d\n' %timestamp)

    csi_len = np.frombuffer(stream, np.uint16, 1, cur)
    if endian_format != 'ieee-le':
        csi_len.dtype = '>u2'
    csi_matrix['csi_len'] = csi_len
    cur = cur + 2
    print ('csi_len is %d\n' %csi_len)

    tx_channel = np.frombuffer(stream, np.uint16, 1, cur)
    if endian_format != 'ieee-le':
        tx_channel.dtype = '>u2'
    csi_matrix['channel'] = tx_channel
    cur = cur + 2
    print('channel is %d\n' % tx_channel)

    err_info = np.frombuffer(stream, np.int8, 1, cur)
    if endian_format != 'ieee-le':
        err_info.dtype = '>u1'
    else:
        err_info.dtype = 'u1'
    csi_matrix['err_info'] = err_info
    cur = cur + 1
    #    print 'err_info is %d\n' %err_info

    noise_floor = np.frombuffer(stream, np.int8, 1, cur)
    if endian_format != 'ieee-le':
        noise_floor.dtype = '>u1'
    else:
        noise_floor.dtype = 'u1'
    csi_matrix['noise_floor'] = noise_floor
    cur = cur + 1
    #    print 'noise_floor is %d\n' %noise_floor

    Rate = np.frombuffer(stream, np.int8, 1, cur)
    if endian_format != 'ieee-le':
        Rate.dtype = '>u1'
    else:
        Rate.dtype = 'u1'
    csi_matrix['Rate'] = Rate
    cur = cur + 1
    #    print 'rate is %x\n' %Rate

    bandWidth = np.frombuffer(stream, np.int8, 1, cur)
    if endian_format != 'ieee-le':
        bandWidth.dtype = '>u1'
    else:
        bandWidth.dtype = 'u1'
    csi_matrix['bandWidth'] = bandWidth
    cur = cur + 1
    #    print 'bandWidth is %d\n' %bandWidth

    num_tones = np.frombuffer(stream, np.int8, 1, cur)
    if endian_format != 'ieee-le':
        num_tones.dtype = ">u1"
    else:
        num_tones.dtype = "u1"
    csi_matrix['num_tones'] = num_tones
    cur = cur + 1
    print('num_tones is %d\n' % num_tones)

    nr = np.frombuffer(stream, np.int8, 1, cur)
    if endian_format != 'ieee-le':
        nr.dtype = '>u1'
    else:
        nr.dtype = 'u1'
    csi_matrix['nr'] = nr
    cur = cur + 1
    # print('nr is %d\n' %nr)
    print('↑↑↑↑↑ (nr) receiving antenna is %d ↑↑↑↑↑↑↑↑' % nr)

    nc = np.frombuffer(stream, np.int8, 1, cur)
    if endian_format != 'ieee-le':
        nc.dtype = '>u1'
    else:
        nc.dtype = 'u1'
    csi_matrix['nc'] = nc
    cur = cur + 1
    # print('nc is %d\n' %nc)
    print('↑↑↑↑↑ (nc) transmitting antenna is %d ↑↑↑↑↑\n\n' % nc)

    rssi = np.frombuffer(stream, np.int8, 1, cur)
    if endian_format != 'ieee-le':
        rssi.dtype = '>u1'
    else:
        rssi.dtype = 'u1'
    csi_matrix['rssi'] = rssi
    cur = cur + 1
    # print ('rssi is %d\n' %rssi)

    rssi1 = np.frombuffer(stream, np.int8, 1, cur)
    if endian_format != 'ieee-le':
        rssi1.dtype = '>u1'
    else:
        rssi1.dtype = 'u1'
    csi_matrix['rssi1'] = rssi1
    cur = cur + 1
    # print ('rssi1 is %d\n' %rssi1)

    rssi2 = np.frombuffer(stream, np.int8, 1, cur)
    if endian_format != 'ieee-le':
        rssi2.dtype = '>u1'
    else:
        rssi2.dtype = 'u1'
    csi_matrix['rssi2'] = rssi2
    cur = cur + 1
    # print ('rssi2 is %d\n' %rssi2)

    rssi3 = np.frombuffer(stream, np.int8, 1, cur)  # wrong
    if endian_format != 'ieee-le':
        rssi3.dtype = '>u1'
    else:
        rssi3.dtype = 'u1'
    csi_matrix['rssi3'] = rssi3
    cur = cur + 1
    # print ('rssi3 is %d\n' %rssi3)

    payload_len = np.frombuffer(stream, np.int16, 1, cur)
    if endian_format != 'ieee-le':
        payload_len.dtype = '>u2'
    csi_matrix['payload_len'] = payload_len
    cur = cur + 2
    # print('payload length is %d\n' %payload_len)

    if csi_len[0] > 0:
        csi_buf = np.frombuffer(stream, np.uint8, csi_len[0], cur)
        csi = read_csi(csi_buf, nr[0], nc[0], num_tones[0])
        cur = cur + csi_len[0]
        csi_matrix['csi'] = csi
    else:
        csi_matrix['csi'] = ''

    if payload_len[0] > 0:
        data_buf = np.frombuffer(stream, np.uint8, payload_len[0], cur)
        cur = cur + payload_len[0]
        csi_matrix['payload'] = data_buf
        # print("%d%d", data_buf)


    else:
        csi_matrix['payload'] = 0

    return csi_matrix


def read_csi(csi_buf, nr, nc, num_tones):
    # print("num_tones %d" %num_tones)
    csi_matrix = np.zeros((nr, nc, 114), dtype=complex)  # create a complex array which store the CSI matrix

    idx = 0
    bits_left = 16  # init bits_left. we process 16 bits at a time
    bitmask = np.uint32((1 << 10) - 1)  # according to the h/w, we have 10 bit resolution
    # for each real and imag value of the csi matrix H
    h_data = csi_buf[idx]  # get 16 bits for processing
    idx += 1
    h_data += (csi_buf[idx] << 8)
    idx += 1
    current_data = h_data & ((np.uint32(1) << 16) - 1)

    for k in range(num_tones):  # loop for every subcarrier
        for nc_idx in range(nc):  # loop for each tx antenna
            for nr_idx in range(nr):  # loop for each rx antenna
                if (bits_left - 10) < 0:
                    h_data = csi_buf[idx]
                    idx += 1
                    h_data += (csi_buf[idx] << 8)
                    idx += 1
                    current_data += h_data << bits_left
                    bits_left += 16
                imag = current_data & bitmask
                imag = bit_convert(imag, 10)
                imag = np.complex(imag)
                imag = imag * (0 + 1j)
                csi_matrix[nr_idx][nc_idx][k] += imag

                bits_left -= 10
                current_data = current_data >> 10

                if (bits_left - 10) < 0:  # bits number less than 10, get next 16 bits
                    h_data = csi_buf[idx]
                    idx += 1
                    h_data += (csi_buf[idx] << 8)
                    idx += 1
                    current_data += h_data << bits_left
                    bits_left += 16

                real = current_data & bitmask
                real = bit_convert(real, 10)
                real = np.complex(real)
                csi_matrix[nr_idx][nc_idx][k] += real

                bits_left -= 10
                current_data = current_data >> 10

    return csi_matrix



print('waiting to connection...（9092）')
while 1:
    data,addr = udpServer.recvfrom(bufsize)  # 接收数据和返回地址
    # count = count + 1

    # testData = base64.b64decode(data)
    # print("消息为：", testData, "地址为", addr)
    printData = read_from_stream(data);
    # print(printData)




    # plt(db(abs(squeeze(data). ')))
    # legend('RX Antenna A', 'RX Antenna B', 'RX Antenna C', 'Location', 'SouthEast');
    # xlabel('Subcarrier index');
    # ylabel('SNR [dB]');

    print("*************************************")
    # print(printData['csi'][0])

    # for i in range(len(printData['csi'])):
    #     print("#####################################")
    #     print(printData['csi'][i])
    #     for t in printData['csi'][i]:
    #         ax1 = subplot( 1, 1, 1)
    #         subplot()
    #         plt.plot(t)
    #         plt.show()

    # print(len(printData['csi'][0][0]))
    # for i in range(len(printData['csi'][0][0])):
    x = arange(0,114,1)
    plt.scatter(printData['csi'][0][0],x)
    plt.scatter(printData['csi'][0][1],x)
    plt.scatter(printData['csi'][1][0],x)
    plt.scatter(printData['csi'][1][1],x)
    plt.show()


    # ax = plt.subplot(111, projection='3d')  # 创建一个三维的绘图工程
    # ax.scatter(printData['csi'][0], c='r')
    # plt.scatter(ax, marker='o')
    # ax.set_zlabel('rs12612420')  # 坐标轴
    # ax.set_ylabel(u'周运动')
    # ax.set_xlabel(u'运动热爱')
    # plt.show()
    print("*************************************")



    # plt(printData)
    # plt.show()


    # with open('data.csi','wb') as f:
    #     f.write(data)

    print("\n")
    print("###########################################################################")
    # date = str(data,"utf-8",errors='ignore');
    # if data == 0:
    #     continue
    # timeArray = time.strptime(date, "%Y-%m-%d %H:%M:%S")
    # timeArray = time.strftime('%Y%m%d%H%M%S',time.localtime(date))
    # timeStamp(date)

