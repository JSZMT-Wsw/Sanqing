# -*- coding: utf-8 -*-
'''
@File  : dust_identify.py
@Author: admin#
@Date  : 2020/12/4 16:15
@Desc  : 
'''

import os
from osgeo import osr
import numpy as np
from IDLApps.SanQing.H8L1Process.H8L1Process import H8L1Process
from src.common.utils.GeoProcessUtil import GeoProcessUtil


def dust_identify(inFile, fillValue, tempFolder):
    """沙尘判识"""

    H8L1ProcessObj = H8L1Process(inFile, fillValue, tempFolder, outMark="ARY")
    # H8L1ProcessObj = H8L1Process(inFile, fillValue, tempFolder)
    # 获取太阳天顶角数据
    soz, XSize, YSize, geotransform = H8L1ProcessObj.doPrase('SOZ')
    idx_day = (soz < 85) & (soz > 0)  # 白天
    idx_night = soz >= 85  # 夜间

    ENII = np.full(soz.shape, fillValue)
    ref047 = H8L1ProcessObj.doPrase(1)[0]
    bt390 = H8L1ProcessObj.doPrase(7)[0]
    bt690 = H8L1ProcessObj.doPrase(9)[0]
    bt860 = H8L1ProcessObj.doPrase(11)[0]
    bt960 = H8L1ProcessObj.doPrase(12)[0]
    bt1040 = H8L1ProcessObj.doPrase(13)[0]
    bt1120 = H8L1ProcessObj.doPrase(14)[0]
    bt1230 = H8L1ProcessObj.doPrase(15)[0]

    # 白天沙尘判识
    # idx_dust_day = (bt1040 - bt1120 <= -1.5) | (bt1120 - bt1230 <= -0.5)
    idx_dust_day = (bt1040 - bt1120 <= -1.2) | (bt1120 - bt1230 <= -0.5)
    idx1 = idx_day & idx_dust_day
    # cloud_day = (ref047 > 0.4) & (bt1120 - bt1230 < -0.5)   # aoddb云判，该方法有误
    # cloud_day = (ref047 > 0.4) & (bt1120 < 270)
    # cloud_day = (ref047 > 0.6) & (bt1120 < 250)
    cloud_day = (ref047 > 0.4) & (bt1120 < 256)

    # 夜间沙尘判识
    idx_dust_night = ((bt1040 - bt1120 <= 0) & (bt1120 - bt1230 <= 0.2)) | (bt1120 - bt1230 < -0.5)  # 中国气象局方案
    # idx_dust_night_2 = (bt390-bt690 > 20) & (bt860-bt1120 > 0)  # 打算作为云判
    # idx_dust_night = ((bt1040 - bt1120 <= 1) & (bt1120 - bt1230 <= 1)) | (bt1120 - bt1230 < 0.5)  # 中国气象局方案
    idx_dust_night_2 = (bt390-bt690 > 15) & (bt860-bt1120 > -0.5)  # 打算作为云判
    idx2 = idx_night & idx_dust_night & idx_dust_night_2

    ENII[idx1] = bt1120[idx1]
    ENII[idx2] = bt1120[idx2]
    ENII[cloud_day] = fillValue
    # ENII[(ENII >= 0) & (ENII < 250)] = 1
    # ENII[(ENII >= 250) & (ENII < 255)] = 2
    # ENII[(ENII >= 255) & (ENII < 260)] = 3
    # ENII[(ENII >= 260) & (ENII < 265)] = 4
    # ENII[(ENII >= 265) & (ENII < 270)] = 5
    # ENII[(ENII >= 270) & (ENII < 275)] = 6
    # # ENII[(ENII >= 275) & (ENII < 280)] = 7
    # # ENII[(ENII >= 280) & (ENII < 285)] = 8
    # # ENII[(ENII >= 285) & (ENII < 290)] = 9
    # # ENII[(ENII >= 290) & (ENII < 350)] = 10
    ENII[(ENII >= 275)] = fillValue
    R = bt1230 - bt1040
    G = bt1040 - bt860
    B = bt1040
    RGB = np.array([R, G, B])

    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)

    outFilePath = tempFolder + "/" + "DUST_" + os.path.basename(os.path.splitext(inFile)[0]) + ".tif"
    GeoProcessUtil.write_tiff(ENII, XSize, YSize, 1, geotransform, sr.ExportToWkt(), out_path=outFilePath,
                              no_data_value=fillValue)

    RGBFilePath = tempFolder + "/" + "RGB_" + os.path.basename(os.path.splitext(inFile)[0]) + ".tif"
    GeoProcessUtil.write_tiff(RGB, XSize, YSize, 3, geotransform, sr.ExportToWkt(), out_path=RGBFilePath,
                              no_data_value=fillValue)



    return outFilePath, RGBFilePath
