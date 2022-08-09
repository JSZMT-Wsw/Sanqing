# -- coding: utf-8 --
import os

from osgeo import osr
import netCDF4 as nc
import numpy as np
from src.common.config.ConstParam import ConstParam
from src.common.process.ProcessBase import BaseProcess
from src.common.utils.FileUtil import BaseFile
from IDLApps.SanQing.Tools.GeoProcessTools import RasterProcess, GdalBase
from src.common.utils.GeoProcessUtil import GeoProcessUtil

def smooth_cloudmask(apr_051):
    d = 0
    for i in range(2000):
        i = i + d
        c = 0
        for j in range(2000):
            jie = j
            j = j + c
            S = []
            # 3x3窗口取值
            for x in range(3):
                for y in range(3):
                    a = i + x
                    b = j + y
                    S.append(apr_051[a, b])
            std_051 = np.std(S)
            c += 2
            if std_051 > 0.02:
                apr_051[a - 2:a + 1, b - 2:b + 1] = -9999
        d += 2

    return apr_051
class HAZE_H8_AHI(BaseProcess):
    '''
    葵花八产品
    '''

    def __init__(self, pluginParam):
        BaseProcess.__init__(self, pluginParam)
        self.isOutExe = False

    def doInnerPy(self):
        try:
            BaseFile.appendLogInfo(self.logPath, "1%", "开始进行算法处理...")
            # xml中的input
            inputFile = self.pluginParam.getInputFile()
            if inputFile is None or BaseFile.isFileOrDir(inputFile) != BaseFile.ISFILE:
                print("输入文件不存在")
                return None
            # p = self.pluginParam.getInputInfoByKey('inputFile1')  # 多个输入
            dependDic = self.pluginParam.getDependFolder()
            ShpFile = dependDic + "/CompShp/AreaNation.shp"
            # shp = r'D:\001project\003WeiFang\RSPlatForm\Depend\WeiFang\Other\othershp\ShanDong.shp'

            fileAry = BaseFile.getFilePathInfo(inputFile, True)
            outFilePath = self.tempFolder + "/" + fileAry[1] + ".tiff"

            nc_data_obj = nc.Dataset(inputFile)
            Lon = nc_data_obj.variables["longitude"][:]
            Lat = nc_data_obj.variables["latitude"][:]
            albedo_04 = nc_data_obj.variables['albedo_04'][:]  # 反照率 0.86μm反照率
            albedo_05 = nc_data_obj.variables['albedo_05'][:]  # 反照率 1.61μm反照率
            albedo_14 = nc_data_obj.variables['tbb_14'][:]  # 反照率 11.23μm
            albedo_15 = nc_data_obj.variables['tbb_15'][:]  # 反照率 12.38μm

            M3 = np.asarray(nc_data_obj.variables['albedo_03'])[:]
            M2 = np.asarray(nc_data_obj.variables['albedo_02'])[:]
            # M1 = np.asarray(nc_data_obj.variables['albedo_01'])[:]
            SOZ = nc_data_obj.variables['SOZ'][:].astype(np.float32)

            YSize = len(Lat)
            XSize = len(Lon)
            LonMin, LatMax, LonMax, LatMin = [Lon.min(), Lat.max(), Lon.max(), Lat.min()]
            Lon_Res = (LonMax - LonMin) / (float(XSize) - 1)
            Lat_Res = (LatMax - LatMin) / (float(YSize) - 1)
            geotransform = (LonMin, Lon_Res, 0, LatMax, 0, -Lat_Res)
            sr = osr.SpatialReference()
            sr.ImportFromEPSG(4326)

            M3 = M3 / np.cos(SOZ * np.pi / 180)
            M2 = M2 / np.cos(SOZ * np.pi / 180)
            apr_051 = M2  # 0.51μm表观反射率

            apr_064 = M3  # 0.64μm表观反射率，红光波段
            apr_086 = albedo_04 / (SOZ * np.pi / 180)  # 0.86μm表观反射率
            apr_161 = albedo_05 / (SOZ * np.pi / 180)  # 1.61μm表观反射率
            apr_1123 = albedo_14 / (SOZ * np.pi / 180)  # 11.23μm
            apr_1238 = albedo_15 / (SOZ * np.pi / 180)  # 12.38μm
            # print(M3, M2)
            haze = (M3 - M2) / (M3 + M2)

            # 4.云/水剔除-------------------------
            # 水体检测(NDVI_LANDSAT8_OLI<0或NDVI<0.1)
            NDVI = (apr_086 - apr_064) / (apr_086 + apr_064)

            # 冰雪检测(NDSI>0.13或NDSI>0.2)
            NDSI = (apr_051 - apr_161) / (apr_051 + apr_161)

            # 云判
            # cloud1 = apr_1123 - apr_1238  # b14-b15 <-0.5 是云
            # cloud_day = (M1 > 0.4) & (apr_1123 < 256)
            apr_051 = smooth_cloudmask(apr_051)

            # NDVI_LANDSAT8_OLI > 0不是水; NDSI < 0.13不是雪   apr_047 <=0.4 不是云
            # idx = np.where((NDVI_LANDSAT8_OLI > 0.1) & (NDSI < 0.13) & (apr_086 <= 0.35) & (cloud1 >= -0.5))  # 1107

            # haze = np.where((NDVI <= 0.1) & (NDSI >= 0.13) & (apr_086 > 0.35) & (cloud_day < -0.5), -2, haze)
            # haze = np.where((NDVI <= 0.1) | (NDSI >= 0.13) | (apr_086 > 0.35) | (apr_051 == -9999), -2, haze)
            # haze = np.where((NDVI <= 0) | (NDSI >= 0.13) | (apr_051 == -9999), -2, haze)
            # haze = np.where((NDVI > 0.1) & (NDSI < 0.13) & (apr_051 != -9999), haze, -2)  # 1124
            haze = np.where((apr_051 != -9999), haze, -2)
            haze[SOZ >= 85] = -2
            # haze[cloud_day] = -2
            # haze[haze < 0] = missing_value
            ds = GdalBase.write_tiff(haze, XSize, YSize, 1, geotransform, sr.ExportToWkt(), out_path=None,
                                           no_data_value=-2, return_mode='MEMORY')

            RasterProcess.clip_by_shp(ds, ShpFile, outFilePath)
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
        # self.areaStatis(tempDir, tifPath, ConstParam.ALLSTATISTICS)

        # 【2】专题图
        curProNumber = curProNumber + 10
        self.creatPic(tifPath, staMap, str(float('%.2f' % curProNumber)))

        # 【3】裁切
        curProNumber = curProNumber + 10
        # self.areaClipTif(tifPath, staMap, str(float('%.2f' % curProNumber)))

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
            self.outStaMap["3clear_cluster_schedule_haze_zonal_histogram"] = {
                "field": "\'issue\', \'region_id\', \'level\', \'value\'", "values": []}
            outStaMapReValues = self.outStaMap["3clear_cluster_schedule_haze_zonal_histogram"]["values"]
            for areaIDRe in staMapRe.keys():
                areaStaRe = staMapRe[areaIDRe]
                for levelStr in areaStaRe.keys():
                    valueStr = str(areaStaRe[levelStr][1])
                    outStaMapReValues.append(issue + "," + areaIDRe + "," + levelStr + "," + valueStr)

        if len(staMap) > 0:
            self.outStaMap["3clear_cluster_schedule_haze_zonal_statistics"] = {
                "field": "\'issue\', \'region_id\', \'MAX\', \'MEAN\', \'MIN\'", "values": []}
            outStaMapValues = self.outStaMap["3clear_cluster_schedule_haze_zonal_statistics"]["values"]
            for areaID in staMap.keys():
                areaSta = staMap[areaID]
                outStaMapValues.append(
                    issue + "," + areaID + "," + str(areaSta[0]) + "," + str(areaSta[1]) + "," + str(areaSta[2]))

