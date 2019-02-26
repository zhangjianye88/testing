# 1ms 接受数据 并做预测
from recvDataThread import recvDataThread
import numpy as np
import math
import time
import datetime
import threading

from scipy.fftpack import fft, ifft
from sklearn.decomposition import PCA
import csv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.externals import joblib
import pickle
import random
# import fft_fea_extrac
# import fft_time2fre as ttf

import feartures_zmt.fft_fea_extrac as fft_fea_extrac
import feartures_zmt.fft_time2fre as ttf

from CSIReader import CSIReader

window_size = 12000  # 12000 12288

slide_size = 200
#  pca_components = 6  # 6 100

ping_time = 0.0012
slice_hz = 5000


class wifiRadar():
    def __init__(self):
        super().__init__()

        self.csiReader = CSIReader()

        self.dataType = 'complex'  # amp 振幅数据  complex 复数数据
        self.predict_data = []

        self.predict_data.append([])
        self.predict_data.append([])
        self.predict_data.append([])
        self.predict_data.append([])

        self.size = window_size
        self.moveWindowSize = slide_size
        self.list = []

        self.inited = False
        self.initSocket()

        # self.clf = self.loadModel()
        self.loadModel_ZMT()
        self.collectionInited = False

        self.plist = []
        self.plist.append([])
        self.plist.append([])
        self.plist.append([])
        self.plist.append([])

        self.lastRecvTime = 0
        self.pCount = 0

        # self.actions = ["somebody", "nobody"]

    # def loadModel(self):
    #     clf = joblib.load("models/2018-09-1718-25/model.m")
    #     return clf

    def loadModel_ZMT(self):
        # print("listsize",self.listsize)
        # modelDir = "./model_zmt/Results_pca_classes2_componets8_window_size14000_inputs30_sitesite05_0920/"
        # modelDir = "./model_zmt/Models_0920_svm_fft_fea13/Results_pca_classes2_componets8_window_size14000_inputs30_sitesite05/"
        # modelDir = "./new_model_zmt/Results_0925_svm_fft_fea_rx2_log/Results_pca_classes2_componets8_window_size10000_inputs114_sitesite05/"
        # modelDir = "./new_model_zmt/Results_0924_svm_fft_fea_rx2/Results_pca_classes2_componets8_window_size10000_inputs114_sitesite05/"
        modelDir = "./models/"
        self.scaler, self.pca, self.loaded_model = load_logi_pca_parameters(modelDir)

    def initSocket(self):
        self.recv = recvDataThread('single')
        self.recv.setCallBack(self.recvAndconvertStrToArr)
        # self.recv.setCallBack(self.recvResolvingCsi)

    def start(self):
        print('start..')
        self.lastRecvTime = time.time()
        self.recv.start()

        # self.tthread = threading.Thread(target=self.test, name='test')
        # self.tthread.start()

    def stop(self):
        self.recv.stop()

    def setPredictCallBack(self, callback):
        self.predictCallBack = callback

    def setPackageCountCallBack(self, callback):
        self.packageCountCallBack = callback

    def recvAndconvertStrToArr(self, data):
        readstr = data.decode('utf-8')  # 这样就直接转换成str格式
        packageArr = readstr.split(";")

        self.pCount = self.pCount + 1  # 统计收到的包数

        # status callback
        if time.time() - self.lastRecvTime >= 1:
            self.lastRecvTime = time.time()
            if self.packageCountCallBack:
                self.packageCountCallBack(self.pCount)
                self.pCount = 0

        if len(packageArr) > 0:
            for strData in packageArr:
                # print(strData)
                ams = strData.split(":")
                # l=len(sdata1)

                sdataList = []

                for am in ams:
                    sdata1 = am.split(",")
                    # 成 float
                    for k in range(len(sdata1)):
                        sdata1[k] = float(sdata1[k])

                    sdataList.append(sdata1)

                self.recvData(sdataList)

    def recvResolvingCsi(self, buffer):
        csi_matrixList = []
        cur = 0
        for i in range(10):  # 一次10包
            csi_matrix = self.csiReader.read_from_stream(buffer, cur)
            # print(np.abs(csi_matrix['csi'][0][0]))
            csi_matrixList.append(csi_matrix)
            cur = cur + 2305

        self.pCount = self.pCount + 1  # 统计收到的包数

        # status callback
        if time.time() - self.lastRecvTime > 1:
            self.lastRecvTime = time.time()
            if self.packageCountCallBack:
                self.packageCountCallBack(self.pCount)
                self.pCount = 0

        for k in range(len(csi_matrixList)):
            csi_matrix = csi_matrixList[k]
            data = np.abs(csi_matrix['csi'][1][0])
            # print("data.shape",data.shape)
            self.recvData(data)

    def recvData(self, amlist):
        # if self.dataType == 'complex':
        #     alist = generateSingleData(sdata)
        # else:
        #     alist = sdata

        # merga data
        amall = []
        for am in amlist:
            amall.extend(am)

        i = 0
        # for i in range(len(amlist)):
        #     am=amlist[i]

        self.predict_data[i].append(amall)

        self.listsize = len(self.predict_data[i])
        if i == 0 and self.listsize < self.size and self.collectionInited == False:
            print(self.listsize)

        if self.listsize > self.size:
            self.collectionInited = True

            amp = np.array(self.predict_data[i][0:self.size])
            print(amp.shape)

            # 获取第二根天线的振幅
            # amp = raw_test[:, 30:60]
            # print("amp shape",amp.shape)
            # amp_reshape = amp.reshape(1,-1)

            time1 = time.time()
            # fre,sigff = ttf.fft_freCut(amp,ping_time)
            index = np.arange(0, 110, 10)

            # fea_fre, fre_eff, sigff_eff = fft_fea_extrac.sigff_fea_extrac(amp,ping_time)
            fea_fre, fre_eff, sigff_eff = fft_fea_extrac.sigff_fea_extrac(amp[:, index] - amp[:, 68:69], ping_time)
            fea_fre2, fre_eff2, sigff_eff2 = fft_fea_extrac.sigff_fea_extrac(
                amp[:, 114 + index] - amp[:, 68 + 114:68 + 114 + 1], ping_time)
            fea_fre3, fre_eff3, sigff_eff3 = fft_fea_extrac.sigff_fea_extrac(
                amp[:, 114 * 2 + index] - amp[:, 68 + 114 * 2:68 + 2 * 114 + 1], ping_time)
            fea_fre4, fre_eff4, sigff_eff4 = fft_fea_extrac.sigff_fea_extrac(
                amp[:, 114 * 3 + index] - amp[:, 68 + 114 * 3:68 + 114 * 3 + 1], ping_time)

            fea_fre.extend(fea_fre2)  # 添加第二根天线的数据
            fea_fre.extend(fea_fre3)
            fea_fre.extend(fea_fre4)

            # fea_fre, fre_eff, sigff_eff = fft_fea_extrac.sigff_fea_extrac(amp)

            self.plist[i].append(fea_fre)
            if len(self.plist[i]) > 10:
                # print("fea_fre.shape",fea_fre.shape)
                # 获取到了频域个特征
                fea_fre_one = self.scaler.transform(self.plist[i])
                fea_fre_pre = self.pca.transform(fea_fre_one)
                # fea_fre_pre= fea_fre_pre_P1[:,1:fea_fre_pre_P1.shape[1]] # 去掉主成分1，zmt,20180919

                y_pred = self.loaded_model.predict(fea_fre_pre)
                time2 = time.time()

                print(i, "     ", y_pred)
                nobodyScore = self.loaded_model.score(fea_fre_pre, np.zeros((fea_fre_pre.shape[0],)))
                somebodyScore = self.loaded_model.score(fea_fre_pre, np.ones((fea_fre_pre.shape[0],)))
                # print("nobody",nobodyScore)
                # print("somebody",somebodyScore)

                if i == 0 and self.predictCallBack:
                    self.predictCallBack(y_pred, somebodyScore, nobodyScore)

                for k in range(self.moveWindowSize):
                    del (self.predict_data[i][0])

                del (self.plist[i][0])


def load_logi_pca_parameters(modelDir):
    # scaler_amp_name = modelDir + "scaler_amp.sav"
    # scaler_amp = pickle.load(open(scaler_amp_name, "rb"))

    scaler_name = modelDir + "scaler.sav"
    scaler = pickle.load(open(scaler_name, "rb"))

    pca_name = modelDir + "pca.sav"
    pca = pickle.load(open(pca_name, "rb"))

    filename = modelDir + "finalized_model.sav"
    loaded_model = pickle.load(open(filename, "rb"))

    return scaler, pca, loaded_model


def generateSingleData(data):
    alist = []
    # 天线一
    for i in range(30):
        realA = int(data[5 + i])
        imagA = int(data[35 + i])
        am = math.sqrt(realA * realA + imagA * imagA)
        alist.append(am)

    # 天线二
    for i in range(30):
        realA = int(data[65 + i])
        imagA = int(data[95 + i])
        am = math.sqrt(realA * realA + imagA * imagA)
        alist.append(am)

    # 天线三
    for i in range(30):
        realA = int(data[125 + i])
        imagA = int(data[155 + i])
        am = math.sqrt(realA * realA + imagA * imagA)
        alist.append(am)

    return alist


def test(self):
    while 1:
        status = random.randint(1, 2)
        if status == 1:
            ypred = np.ones(10)
            self.predictCallBack(ypred, 1, 0)
        else:
            ypred = np.zeros(10)
            self.predictCallBack(ypred, 1, 0)

        time.sleep(1)