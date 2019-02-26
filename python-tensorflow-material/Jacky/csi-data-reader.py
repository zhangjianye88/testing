import socket
import time
import numpy as np

import base64

with open('data.csi', 'rb') as f:
    image_data = f.read()
    base64_data = base64.b64encode(image_data)  # 使用 base64 编码
    print(image_data)
    print(base64_data)

file_path = "./data.csi"


#
# @brief read the logged data which could saved from the client or saved from the server
# @return return a dictionary in which contains the CSI_matrix
#

def read_csi(self, csi_buf, nr, nc, num_tones):
    if nr <= 0 or nc <= 0:
        return
    # create a complex array which store the CSI matrix
    csi_matrix = np.zeros((3, 3, 114), dtype=complex)
    temp = []
    idx = 0
    bits_left = 16  # init bits_left. we process 16 bits at a time
    # according to the h/w, we have 10 bit resolution
    bitmask = np.uint32((1 << 10) - 1)
    # for each real and imag value of the csi matrix H
    h_data = csi_buf[idx]  # get 16 bits for processing
    idx += 1
    h_data += (csi_buf[idx] << 8)
    idx += 1
    current_data = h_data & ((np.uint32(1) << 16) - 1)

    for k in range(num_tones[0]):  # loop for every subcarrier
        for nc_idx in range(nc[0]):  # loop for each tx antenna
            for nr_idx in range(nr[0]):  # loop for each rx antenna
                if (bits_left - 10) < 0:
                    h_data = csi_buf[idx]
                    idx += 1
                    h_data += (csi_buf[idx] << 8)
                    idx += 1
                    current_data += h_data << bits_left
                    bits_left += 16
                imag = current_data & bitmask
                imag = bit_convert(imag, 10)
                x = imag
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
                temp.append(real)
                temp.append(x)
                real = np.complex(real)
                csi_matrix[nr_idx][nc_idx][k] += real
                bits_left -= 10
                current_data = current_data >> 10

    # print(temp)
    return csi_matrix

def read_from_file(self,file_path):
    try:
        file = open(file_path, 'rb')
    except Exception:
        # print('couldn\'t open file %s' % file_path)
        # file.close()
        sys.exit(0)

    status = file.seek(0, 2)
    if status != 0:
        pass  # error message
        # ##print 'Error2'

    len = file.tell()
    # ##print 'file length is:%d\n' %len

    status = file.seek(0, 0)
    if status != 0:
        pass  # error message
        # ##print status
        # ##print 'error3'

    cur = 0
    ret = []

    # some embedded system use big endian. for 16/32/64 system this should be all fine
    endian_format = 'ieee-be'

    while cur < (len - 4):

        csi_matrix = {}
        field_len = np.fromfile(file, np.uint16, 1)
        if endian_format != 'ieee-be':
            field_len.dtype = '>u2'
        cur = cur + 2
        # print('Block length is: %d\n' % field_len)

        if (cur + field_len) > len:
            break

        timestamp = np.fromfile(file, np.uint64, 1)
        if endian_format != 'ieee-be':
            timestamp.dtype = '>u8'
        csi_matrix['timestamp'] = timestamp
        cur = cur + 8
        # print('timestamp is %d\n' % timestamp)

        csi_len = np.fromfile(file, np.uint16, 1)
        if endian_format != 'ieee-be':
            csi_len[0].dtype = '>u2'
        csi_matrix['csi_len[0]'] = csi_len[0]
        cur = cur + 2
        # print('csi_len[0] is %d\n' % csi_len[0])

        tx_channel = np.fromfile(file, np.uint16, 1)
        if endian_format != 'ieee-be':
            tx_channel.dtype = '>u2'
        csi_matrix['channel'] = tx_channel
        cur = cur + 2
        # print('channel is %d\n' % tx_channel)

        err_info = np.fromfile(file, np.int8, 1)
        if endian_format != 'ieee-be':
            err_info.dtype = '>u1'
        else:
            err_info.dtype = 'u1'
        csi_matrix['err_info'] = err_info
        cur = cur + 1
        # print('err_info is %d\n' % err_info)

        noise_floor = np.fromfile(file, np.int8, 1)
        if endian_format != 'ieee-be':
            noise_floor.dtype = '>u1'
        else:
            noise_floor.dtype = 'u1'
        csi_matrix['noise_floor'] = noise_floor
        cur = cur + 1
        # print('noise_floor is %d\n' % noise_floor)

        Rate = np.fromfile(file, np.int8, 1)
        if endian_format != 'ieee-be':
            Rate.dtype = '>u1'
        else:
            Rate.dtype = 'u1'
        csi_matrix['Rate'] = Rate
        cur = cur + 1
        # print('rate is %x\n' % Rate[0])

        bandWidth = np.fromfile(file, np.int8, 1)
        if endian_format != 'ieee-be':
            bandWidth.dtype = '>u1'
        else:
            bandWidth.dtype = 'u1'
        csi_matrix['bandWidth'] = bandWidth
        cur = cur + 1
        # print('bandWidth is %d\n' % bandWidth)

        num_tones = np.fromfile(file, np.int8, 1)
        if endian_format != 'ieee-be':
            num_tones.dtype = ">u1"
        else:
            num_tones.dtype = "u1"
        csi_matrix['num_tones'] = num_tones
        cur = cur + 1
        # print('num_tones is %d\n' % num_tones)

        nr = np.fromfile(file, np.int8, 1)
        if endian_format != 'ieee-be':
            nr.dtype = '>u1'
        else:
            nr.dtype = 'u1'
        csi_matrix['nr'] = nr
        cur = cur + 1
        print('nr is %d\n' % nr)

        nc = np.fromfile(file, np.int8, 1)
        if endian_format != 'ieee-be':
            nc.dtype = '>u1'
        else:
            nc.dtype = 'u1'
        csi_matrix['nc'] = nc
        cur = cur + 1
        print('nc is %d\n' % nc)

        rssi = np.fromfile(file, np.int8, 1)
        if endian_format != 'ieee-be':
            rssi.dtype = '>u1'
        else:
            rssi.dtype = 'u1'
        csi_matrix['rssi'] = rssi
        cur = cur + 1
        # print('rssi is %d\n' % rssi)

        rssi1 = np.fromfile(file, np.int8, 1)
        if endian_format != 'ieee-be':
            rssi1.dtype = '>u1'
        else:
            rssi1.dtype = 'u1'
        csi_matrix['rssi1'] = rssi1
        cur = cur + 1
        # print('rssi1 is %d\n' % rssi1)

        rssi2 = np.fromfile(file, np.int8, 1)
        if endian_format != 'ieee-be':
            rssi2.dtype = '>u1'
        else:
            rssi2.dtype = 'u1'
        csi_matrix['rssi2'] = rssi2
        cur = cur + 1
        # print('rssi2 is %d\n' % rssi2)

        rssi3 = np.fromfile(file, np.int8, 1)  # wrong
        if endian_format != 'ieee-be':
            rssi3.dtype = '>u1'
        else:
            rssi3.dtype = 'u1'
        csi_matrix['rssi3'] = rssi3
        cur = cur + 1
        # print('rssi3 is %d\n' % rssi3)

        payload_len = np.fromfile(file, np.int16, 1)
        if endian_format != 'ieee-be':
            payload_len.dtype = '>u2'
        csi_matrix['payload_len'] = payload_len
        cur = cur + 2
        # print('payload length is %d\n' % payload_len)

        if csi_len[0] > 0:
            csi_buf = np.fromfile(file, np.uint8, csi_len[0])
            # print("            nc:"+nc+"             nr"+nr)
            csi = read_csi(csi_buf, nr, nc, num_tones)
            cur = cur + csi_len[0]
            csi_matrix['csi'] = csi
#        else:
#            csi_matrix['csi'] =''

        if payload_len > 0:
            data_buf = np.fromfile(file, np.uint8, payload_len[0])
            cur = cur + payload_len
            csi_matrix['payload'] = data_buf
        else:
            csi_matrix['payload'] = 0

        if (cur + 420) > len:
            break
        ret.append(csi_matrix)

    if ret.__len__() > 1:
        ret = ret[0:(ret.__len__() - 1)]

    file.close()
    return ret

test1 = read_from_file('',file_path)
print(test1)
