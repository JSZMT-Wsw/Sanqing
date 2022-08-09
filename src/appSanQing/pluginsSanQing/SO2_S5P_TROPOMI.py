# -- coding: utf-8 --
import os
import numpy as np
import netCDF4 as nc
import h5py
from osgeo import osr
from src.common.config.ConstParam import ConstParam
from src.common.process.ProcessBase import BaseProcess
from src.common.utils.FileUtil import BaseFile
from IDLApps.SanQing.Tools.GeoProcessTools import RasterProcess
from src.common.utils.GeoProcessUtil import GeoProcessUtil
from IDLApps.SanQing.S5PL2Process.S5PL2Process import S5PL2Process


class SO2_S5P_TROPOMI(BaseProcess):
    '''
    哨兵5产品
    '''

    def __init__(self, pluginParam):
        BaseProcess.__init__(self, pluginParam)
        self.isOutExe = False

    def doInnerPy(self):
        try:
            BaseFile.appendLogInfo(self.logPath, "1%", "开始进行算法处理...")

            inputFile = self.pluginParam.getInputFile()
            if inputFile is None or BaseFile.isFileOrDir(inputFile.split(';')[0]) != BaseFile.ISFILE:
                print("输入文件不存在")
                return None

            issue = self.pluginParam.getIssue()
            model = 1
            fillValue = float(self.pluginParam.getFillValue())
            dependFolder = self.pluginParam.getDependFolder()
            shpPath = dependFolder + "/" + "CompShp" + "/" + "AreaNation.shp"

            S5PL2ProcessObj = S5PL2Process(issue, inputFile, "SO2", model, fillValue, shpPath, self.tempFolder)
            outFilePath = S5PL2ProcessObj.doPrase()
            self.rsOutMap['OUTFILEPATH'] = outFilePath
            print("------------------------")
        except:
            BaseFile.appendLogInfo(self.logPath, "90%", 'faild')
            return False

    def doStatisComp(self, tempDir, tifPath, curProNumber):
        """统计分析"""
        staMap = self.dostaMapInit(tifPath)

        # #【1】统计，【临时文件夹，tif文件，最小的行政区划，区域的等级】
        # ConstParam.NORMALSTATISTICS（正常统计）, ConstParam.GRADATIONSTATISTICS（分级统计）, ConstParam.ALLSTATISTICS（分级统计 + 正常统计）
        self.areaStatis(tempDir, tifPath, ConstParam.ALLSTATISTICS)

        # 【2】专题图
        curProNumber = curProNumber + 10
        self.creatPic(tifPath, staMap, str(float('%.2f' % curProNumber)))

        # 【3】裁切
        curProNumber = curProNumber + 10
        self.areaClipTif(tifPath, staMap, str(float('%.2f' % curProNumber)))

        return True

    def updateStaMapInfo(self, staMapInfo):
        """更新统计信息 staMaps["StaMapRe"]结构 [AreaID][Level]=row  staMaps["StaMap"]结构 [AreaID]=row"""
        # 【0】寻找统计结果字典
        if "StaMapRe" in staMapInfo:
            staMapRe = staMapInfo["StaMapRe"]
        else:
            staMapRe = {}

        if "StaMap" in staMapInfo:
            staMap = staMapInfo["StaMap"]
        else:
            staMap = {}

        issue = self.pluginParam.getIssue()
        if len(staMapRe) > 0:
            self.outStaMap["3clear_cluster_schedule_so2_zonal_histogram"] = {
                "field": "\'issue\', \'region_id\', \'level\', \'value\'", "values": []}
            outStaMapReValues = self.outStaMap["3clear_cluster_schedule_so2_zonal_histogram"]["values"]
            for areaIDRe in staMapRe.keys():
                areaStaRe = staMapRe[areaIDRe]
                for levelStr in areaStaRe.keys():
                    valueStr = str(areaStaRe[levelStr][1])
                    outStaMapReValues.append(issue + "," + areaIDRe + "," + levelStr + "," + valueStr)

        if len(staMap) > 0:
            self.outStaMap["3clear_cluster_schedule_so2_zonal_statistics"] = {
                "field": "\'issue\', \'region_id\', \'MAX\', \'MEAN\', \'MIN\'", "values": []}
            outStaMapValues = self.outStaMap["3clear_cluster_schedule_so2_zonal_statistics"]["values"]
            for areaID in staMap.keys():
                areaSta = staMap[areaID]
                outStaMapValues.append(
                    issue + "," + areaID + "," + str(areaSta[0]) + "," + str(areaSta[1]) + "," + str(areaSta[2]))


