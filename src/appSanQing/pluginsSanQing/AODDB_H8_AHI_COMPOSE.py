# -*- coding: utf-8 -*-
'''
@File  : PM25_H8_AHI.py
@Author: admin#
@Date  : 2020/11/19 17:35
@Desc  : 
'''

import os
from src.common.config.ConstParam import ConstParam
from src.common.process.ProcessBase import BaseProcess
from src.common.utils.FileUtil import BaseFile
from src.common.utils.GeoProcessUtil import GeoProcessUtil



class AODDB_H8_AHI_COMPOSE(BaseProcess):
    '''
    H8_AHI合成产品
    '''

    def __init__(self, pluginParam):
        BaseProcess.__init__(self, pluginParam)
        self.isOutExe = False

    def doInnerPy(self):
        try:
            BaseFile.appendLogInfo(self.logPath, "1%", "开始进行算法处理...")
            inputFile = self.pluginParam.getInputFile()
            if inputFile is None or BaseFile.isFileOrDir(inputFile.split(',')[0]) != BaseFile.ISFILE:
                print("输入文件不存在")
                return None
            inputFile_list = [x for x in inputFile.split(',')]
            outFilePath = self.tempFolder + "/" + self.pluginParam.getPluginName() + str(self.pluginParam.getIssue()) + str(self.pluginParam.getCycle()) + ".tiff"
            fillValue = float(self.pluginParam.getFillValue())
            GeoProcessUtil.raster_compose(inputFile_list, outFilePath, fillValue, "MEAN")
            self.rsOutMap['OUTFILEPATH'] = outFilePath
        except Exception as e:
            BaseFile.appendLogInfo(self.logPath, "90%", e.message)
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
            self.outStaMap["3clear_cluster_schedule_aoddb_compose_zonal_histogram"] = {
                "field": "\'issue\', \'region_id\', \'level\', \'value\'", "values": []}
            outStaMapReValues = self.outStaMap["3clear_cluster_schedule_aoddb_compose_zonal_histogram"]["values"]
            for areaIDRe in staMapRe.keys():
                areaStaRe = staMapRe[areaIDRe]
                for levelStr in areaStaRe.keys():
                    valueStr = str(areaStaRe[levelStr][1])
                    outStaMapReValues.append(issue + "," + areaIDRe + "," + levelStr + "," + valueStr)

        if len(staMap) > 0:
            self.outStaMap["3clear_cluster_schedule_aoddb_compose_zonal_statistics"] = {
                "field": "\'issue\', \'region_id\', \'MAX\', \'MEAN\', \'MIN\'", "values": []}
            outStaMapValues = self.outStaMap["3clear_cluster_schedule_aoddb_compose_zonal_statistics"]["values"]
            for areaID in staMap.keys():
                areaSta = staMap[areaID]
                outStaMapValues.append(
                    issue + "," + areaID + "," + str(areaSta[0]) + "," + str(areaSta[1]) + "," + str(areaSta[2]))


