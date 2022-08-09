# -- coding: utf-8 --

import os

import numpy as np
import netCDF4 as nc
from osgeo import osr
from src.common.config.ConstParam import ConstParam
from src.common.process.ProcessBase import BaseProcess
from src.common.utils.FileUtil import BaseFile
from src.common.utils.GeoProcessUtil import GeoProcessUtil
from IDLApps.SanQing.H8L1Process.H8L1Process import H8L1Process
from IDLApps.SanQing.DUST_H8_AHI.dust_identify import dust_identify
from IDLApps.SanQing.H8L2Process.H8L2Process import H8L2Process


class DUST_H8_AHI(BaseProcess):
    '''
    H8_AHI产品
    '''

    def __init__(self, pluginParam):
        BaseProcess.__init__(self, pluginParam)
        self.isOutExe = False

    def doInnerPy(self):
        try:
            BaseFile.appendLogInfo(self.logPath, "1%", "开始进行算法处理...")
            inputFile = self.pluginParam.getInputFile()
            if inputFile is None or BaseFile.isFileOrDir(inputFile) != BaseFile.ISFILE:
                print("输入文件不存在")
                return None
            # 沙尘、RGB三通道tif生产
            fillValue = float(self.pluginParam.getFillValue())
            outFilePath, RGBFilePath = dust_identify(inputFile, fillValue, self.tempFolder)
            # outFilePath = r"D:\Proj\TempFolder\1610695399509\DUST_NC_H08_20210113_0400_R21_FLDK.06001_06001.tif"
            # RGBFilePath = r"D:\Proj\TempFolder\1610695399509\RGB_NC_H08_20210113_0400_R21_FLDK.06001_06001.tif"
            # 云分类tif生产
            # CLPFilePath = self.pluginParam.getInputInfoByKey('inputCLPFile')
            # H8L2Obj = H8L2Process(CLPFilePath, "CLP", fillValue, self.tempFolder, outMark="TIF")
            # CLTFilePath, XSize, YSize, geotransform = H8L2Obj.doPrase()

            self.rsOutMap['OUTFILEPATH'] = outFilePath
            # self.rgbFile = {'H8RGB': RGBFilePath}
            # self.lyrFile = {'CLT': CLTFilePath}
        except:
            BaseFile.appendLogInfo(self.logPath, "90%", 'faild')
            return False

    def doStatisComp(self, tempDir, tifPath, curProNumber):
        """统计分析"""
        staMap = self.dostaMapInit(tifPath)
        # areaIDList = self.pluginParam.getALLAreaIDList(self.curAreaInfo)
        # Nan = ['Nan'] * len(areaIDList)
        # staMap = dict(zip(areaIDList, Nan))

        # staMap = self.dostaMapInit(CLTFilePath)

        # #【1】统计，【临时文件夹，tif文件，最小的行政区划，区域的等级】
        # ConstParam.NORMALSTATISTICS（正常统计）, ConstParam.GRADATIONSTATISTICS（分级统计）, ConstParam.ALLSTATISTICS（分级统计 + 正常统计）
        # self.areaStatis(tempDir, tifPath, ConstParam.ALLSTATISTICS)

        # 【2】专题图
        curProNumber = curProNumber + 10
        self.creatPic(tifPath, staMap, str(float('%.2f' % curProNumber)))

        # 【3】裁切
        curProNumber = curProNumber + 10
        # self.areaClipTif(tifPath, staMap, str(float('%.2f' % curProNumber)))

        return True

