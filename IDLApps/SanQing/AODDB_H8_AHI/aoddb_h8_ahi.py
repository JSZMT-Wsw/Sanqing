# -*- coding: utf-8 -*-
'''
@File  : aoddb_h8_ahi.py
@Author: admin#
@Date  : 2020/11/19 13:48
@Desc  : 
'''
import os
import numpy as np
from netCDF4 import Dataset
from osgeo import osr
from tqdm import tqdm
from scipy import signal
from src.common.utils.GeoProcessUtil import GeoProcessUtil
from src.common.utils.FileUtil import BaseFile


def get_ref(sunzenith, albedo):
    # 计算表观反射率
    return albedo / np.cos(sunzenith * np.pi / 180)


# 云识别,去除边缘的云，计算3x3窗口像元的标准差，
# 1.STD_0.51μm > 0.006；
# 2.STD_0.47μm > 0.02；
# 3.STD_11.2μm > 4.5
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


def CalAOD(LUTDatas, soz, saz, rela, apr, ref):
    """计算AOD"""

    aodValue = [0.0001, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]  # 550nm气溶胶光学厚度
    asol = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72]  # 太阳天顶角
    avis = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84]  # 卫星天顶角
    phiv = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144, 156, 168, 180]  # 太阳方位角(卫星方位角为0，即相对方位角为O．180)

    asolnum = len(asol)
    avisnum = len(avis)
    phivnum = len(phiv)
    enum = asolnum * avisnum * phivnum

    asolgab = asol[1] - asol[0]  # 太阳天顶角 间隔
    avisgab = avis[1] - avis[0]  # 观测天顶角 间隔
    phivgab = phiv[1] - phiv[0]  # 相对方位角 间隔

    if soz % asolgab == 0:
        soz += 0.01
    if saz % avisgab == 0:
        saz += 0.01
    if rela % phivgab == 0:
        rela += 0.01

    x = int(soz / asolgab)
    y = int(saz / avisgab)
    z = int(rela / phivgab)

    # 8条记录的行号   卫星天顶角asolnum 观测天顶角avisnum 相对方位角phivnum   每12*13*16=2496次一个aod值循环
    f_apr = []
    for i in range(len(aodValue)):  # aod值有x个值
        d1 = (x * avisnum * phivnum + y * phivnum + z) + enum * i
        d2 = (x * avisnum * phivnum + y * phivnum + (z + 1)) + enum * i
        d3 = (x * avisnum * phivnum + (y + 1) * phivnum + z) + enum * i
        d4 = (x * avisnum * phivnum + (y + 1) * phivnum + (z + 1)) + enum * i
        d5 = ((x + 1) * avisnum * phivnum + y * phivnum + z) + enum * i
        d6 = ((x + 1) * avisnum * phivnum + y * phivnum + (z + 1)) + enum * i
        d7 = ((x + 1) * avisnum * phivnum + (y + 1) * phivnum + z) + enum * i
        d8 = ((x + 1) * avisnum * phivnum + (y + 1) * phivnum + (z + 1)) + enum * i

        # 相对方位角
        deg_1 = (rela % phivgab) / float(phivgab)
        intp1 = np.array(LUTDatas[d1]) + (np.array(LUTDatas[d2]) - np.array(LUTDatas[d1])) * deg_1
        intp2 = np.array(LUTDatas[d3]) + (np.array(LUTDatas[d4]) - np.array(LUTDatas[d3])) * deg_1
        intp3 = np.array(LUTDatas[d5]) + (np.array(LUTDatas[d6]) - np.array(LUTDatas[d5])) * deg_1
        intp4 = np.array(LUTDatas[d7]) + (np.array(LUTDatas[d8]) - np.array(LUTDatas[d7])) * deg_1

        # 卫星天顶角
        deg_2 = (saz % avisgab) / float(avisgab)
        intp5 = intp1 + (intp2 - intp1) * deg_2
        intp6 = intp3 + (intp4 - intp3) * deg_2

        # 太阳天顶角
        deg_3 = (soz % asolgab) / float(asolgab)
        intp = intp5 + (intp6 - intp5) * deg_3

        S = intp[0]
        TT = intp[1]
        rho = intp[2]
        f_apr.append(rho + TT * ref / (1 - S * ref))

    aod = np.interp(apr, f_apr, aodValue)

    return aod


def aoddb_h8_ahi(issue, h8_l1_file, shp_file, fillValue, lutFolder, tempFolder):
    """H8 深蓝算法"""
    nc_data = Dataset(h8_l1_file)

    albedo_01 = nc_data.variables['albedo_01'][:]  # 反照率 蓝光波段反照率，0.47μm
    albedo_02 = nc_data.variables['albedo_02'][:]  # 反照率 0.51μm反照率
    albedo_03 = nc_data.variables['albedo_03'][:]  # 反照率 红光波段反照率，0.64μm
    albedo_04 = nc_data.variables['albedo_04'][:]  # 反照率 0.86μm反照率
    albedo_05 = nc_data.variables['albedo_05'][:]  # 反照率 1.61μm反照率
    albedo_06 = nc_data.variables['albedo_06'][:]  # 反照率 近红外波段反照率，2.3μm

    SOZ = nc_data.variables['SOZ'][:].astype(np.float32)  # 太阳天顶角
    SAZ = nc_data.variables['SAZ'][:].astype(np.float32)  # 卫星天顶角
    SOA = nc_data.variables['SOA'][:].astype(np.float32)  # 太阳方位角
    SAA = nc_data.variables['SAA'][:].astype(np.float32)  # 卫星方位角

    rela = abs(SOA - SAA)
    rela = np.where(rela > 180, rela - 180, rela)  # 相对方位角

    # 经纬度
    latitude = nc_data.variables['latitude'][:]
    longitude = nc_data.variables['longitude'][:]

    nc_data.close()

    # 2.计算表观反射率-------------------------
    apr_047 = get_ref(SOZ, albedo_01)  # 0.47μm表观反射率，蓝光波段
    apr_051 = get_ref(SOZ, albedo_02)  # 0.51μm表观反射率，绿光波段
    apr_064 = get_ref(SOZ, albedo_03)  # 0.64μm表观反射率，红光波段
    apr_086 = get_ref(SOZ, albedo_04)  # 0.86μm表观反射率
    apr_161 = get_ref(SOZ, albedo_05)  # 1.61μm表观反射率
    apr_230 = get_ref(SOZ, albedo_06)  # 2.3μm表观反射率，近红外波段

    # 3.计算地表反射率-------------------------
    fi = 1 / -1 * np.cos(SOZ * np.pi / 180) * np.cos(SAZ * np.pi / 180) + np.sin(SOZ * np.pi / 180) * np.sin(
        SAZ * np.pi / 180) * np.cos(rela)  # 散射角
    ref_064 = (0.262 + 0.0021 * fi) * apr_230 + (0.03 - 0.0003 * fi)
    ref_047 = 0.519 * ref_064 + 0.0006

    # 4.云/水剔除-------------------------
    # 水体检测(NDVI_LANDSAT8_OLI<0或NDVI<0.1)
    NDVI = (apr_086 - apr_064) / (apr_086 + apr_064)

    # 冰雪检测(NDSI>0.13或NDSI>0.2)
    NDSI = (apr_051 - apr_161) / (apr_051 + apr_161)

    # NDVI_LANDSAT8_OLI > 0不是水; NDSI < 0.13不是雪   apr_047 <=0.4 不是云
    # idx = np.where((NDVI_LANDSAT8_OLI > 0.1) & (NDSI < 0.13) & (apr_086 <= 0.35) & (cloud1 >= -0.5))  # 1107

    # 云识别：3x3窗口标准差
    apr_051 = smooth_cloudmask(apr_051)
    idx = np.where((NDVI > 0.1) & (NDSI < 0.13) & (apr_051 != -9999))  # 1124

    locations = list(zip(idx[0], idx[1]))

    minLon, maxLon, minLat, maxLat = 111, 123, 34, 41  # 中国区范围

    XSize = len(longitude)
    YSize = len(latitude)
    LonMin, LatMax, LonMax, LatMin = [longitude.min(), latitude.max(), longitude.max(), latitude.min()]
    Lon_Res = (LonMax - LonMin) / (float(XSize) - 1)
    Lat_Res = (LatMax - LatMin) / (float(YSize) - 1)

    # 5.匹配数据与查找表的时间（根据月份匹配查找表）
    LUTFile = lutFolder + "/" + 'H8_LUT_BLUE' + issue[4:6] + '.txt'

    # 6.根据查找表插值计算AOD并裁剪中国区-------------------------
    with open(LUTFile, 'r') as f:
        LUTDatas = f.readlines()
    LUTDatas = [line.strip().split() for line in LUTDatas]
    LUTDatas = [list(map(float, line)) for line in LUTDatas]

    aod = np.full(ref_047.shape, fillValue)
    for pos in tqdm(locations):

        if SOZ[pos] >= 72:
            continue
        if SAZ[pos] >= 84:
            continue

        lon = LonMin + pos[1] * Lon_Res
        lat = LatMax - pos[0] * Lat_Res
        if minLon <= lon <= maxLon and minLat <= lat <= maxLat:
            aod[pos] = CalAOD(LUTDatas, SOZ[pos], SAZ[pos], rela[pos], apr_047[pos], ref_047[pos])

    aod[aod < 0.0001] = fillValue

    # 增加平滑
    aod[aod < 0] = np.NAN
    step = 2
    # for i in range(step, aod.shape[0]-step):
    #     for j in range(step, aod.shape[1]-step):
    #         aod[i, j] = np.nanmean(aod[i - step: i + step, j - step: j + step])
    aod[np.isnan(aod)] = fillValue

    geotransform = (LonMin, Lon_Res, 0, LatMax, 0, -Lat_Res)
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)

    fileAry = BaseFile.getFilePathInfo(h8_l1_file, True)
    aodFile = tempFolder + "/" + fileAry[1] + ".tif"
    ds = GeoProcessUtil.write_tiff(aod, XSize, YSize, 1, geotransform, sr.ExportToWkt(), out_path=None,
                                   no_data_value=fillValue)
    GeoProcessUtil.clip_by_shp(ds, shp_file, aodFile)

    return aodFile
