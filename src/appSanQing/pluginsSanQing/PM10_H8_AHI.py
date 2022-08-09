# -*- coding: utf-8 -*-
'''
@File  : PM25_H8_AHI.py
@Author: admin#
@Date  : 2020/11/19 17:35
@Desc  : 
'''
import os
import glob
import numpy as np
from src.common.config.ConstParam import ConstParam
from src.common.process.ProcessBase import BaseProcess
from src.common.utils.FileUtil import BaseFile
from src.common.utils.GeoProcessUtil import GeoProcessUtil
from IDLApps.SanQing.PM10_H8_AHI.PM10_H8_AHI import get_sample_data, rf_model_fit, rf_model_predict, \
    rf_pred_accuracy_scatter


class PM10_H8_AHI(BaseProcess):
    '''
    H8_AHI产品
    '''

    def __init__(self, pluginParam):
        BaseProcess.__init__(self, pluginParam)
        self.isOutExe = False

    def doInnerPy(self):
        try:
            BaseFile.appendLogInfo(self.logPath, "1%", "开始进行算法处理...")

            ARPFiles = [x.strip() for x in self.pluginParam.getInputInfoByKey('ARPFiles').split(";")]
            STNFiles = [x.strip() for x in self.pluginParam.getInputInfoByKey('STNFiles').split(";")]
            QXFiles = [x.strip() for x in self.pluginParam.getInputInfoByKey('QXFiles').split(";")]

            curARPFile = self.pluginParam.getInputInfoByKey('curARPFile')
            curSTNFile = self.pluginParam.getInputInfoByKey('curSTNFile')
            curQXFile = self.pluginParam.getInputInfoByKey('curQXFile')

            stn_features = ['PM10']
            qx_features = ['relHum', 'vis', 'windSpd2m', 'windDir2m', 'airTemp', 'staPrss']
            aod_features = ['AOD']

            issue = self.pluginParam.getIssue()
            curIDLAppsFolder = self.pluginParam.getIDLAppFolder() + "/" + self.name
            model_file_old = glob.glob(curIDLAppsFolder + "/" + "model_*.pkl")
            if len(model_file_old) == 0:
                model_file_old = None
            else:
                model_file_old = model_file_old[-1]

            model_file_new = curIDLAppsFolder + "/model_" + issue + ".pkl"
            model_file = model_file_old

            model_plot = curIDLAppsFolder + "/model_plot.png"
            model_scatter = curIDLAppsFolder + "/model_scatter.png"
            pred_scatter = self.curProdFolder + "/" + "pred_" + issue + ".png"

            dependDic = self.pluginParam.getDependFolder()
            # CityShpFile = dependDic + "/CompShp/AreaCity.shp"
            fileShp = dependDic + "/Other/othershp/AreaNation.shp"

            fillValue = float(self.pluginParam.getFillValue())

            flag = self.pluginParam.getInputInfoByKey('flag')  # 是否需要训练新模型
            if flag == str(True) or flag == str('true'):
                out_df = get_sample_data(ARPFiles, STNFiles, QXFiles, aod_features, stn_features, qx_features)
                rf_model_fit(out_df, qx_features, aod_features, stn_features, model_file_new, model_plot, model_scatter)
                model_file = model_file_new

            if BaseFile.isFileOrDir(model_file) == BaseFile.ISFILE:
                pm10, XSize, YSize, geotrans, proj = rf_model_predict(issue, model_file, fileShp, curARPFile,
                                                                      curQXFile, qx_features, self.tempFolder,
                                                                      fillValue)
                # 增加平滑
                pm10[pm10 < 0] = np.NAN
                step = 2
                for i in range(step, pm10.shape[0] - step):
                    for j in range(step, pm10.shape[1] - step):
                        pm10[i, j] = np.nanmean(pm10[i - step:i + step, j - step:j + step])

                pm10[np.isnan(pm10)] = fillValue

                outFilePath = self.tempFolder + "/" + issue + ".tif"
                GeoProcessUtil.write_tiff(pm10, XSize, YSize, 1, geotrans, proj, out_path=outFilePath,
                                          no_data_value=fillValue)

                # rf_pred_accuracy_scatter(issue, pm10, geotrans, curSTNFile, stn_features, pred_scatter)
                self.rsOutMap['OUTFILEPATH'] = outFilePath

            else:
                print('model is not fit, and old model is not exit')
                print('please fit RF model, flag=True')
                return
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
            self.outStaMap["3clear_cluster_schedule_pm10_zonal_histogram"] = {
                "field": "\'issue\', \'region_id\', \'level\', \'value\'", "values": []}
            outStaMapReValues = self.outStaMap["3clear_cluster_schedule_pm10_zonal_histogram"]["values"]
            for areaIDRe in staMapRe.keys():
                areaStaRe = staMapRe[areaIDRe]
                for levelStr in areaStaRe.keys():
                    valueStr = str(areaStaRe[levelStr][1])
                    outStaMapReValues.append(issue + "," + areaIDRe + "," + levelStr + "," + valueStr)

        if len(staMap) > 0:
            self.outStaMap["3clear_cluster_schedule_pm10_zonal_statistics"] = {
                "field": "\'issue\', \'region_id\', \'MAX\', \'MEAN\', \'MIN\'", "values": []}
            outStaMapValues = self.outStaMap["3clear_cluster_schedule_pm10_zonal_statistics"]["values"]
            for areaID in staMap.keys():
                areaSta = staMap[areaID]
                outStaMapValues.append(
                    issue + "," + areaID + "," + str(areaSta[0]) + "," + str(areaSta[1]) + "," + str(areaSta[2]))


