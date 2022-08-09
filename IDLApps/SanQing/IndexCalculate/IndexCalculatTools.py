# -*-- coding: UTF-8 -*-
"""
@author: DYX
@file:IndexCalculatTools.py
@time:2019/11/516:44
@desc:
"""

from __future__ import division
import xlrd
import xlwt
import numpy as np
from src.common.utils.GeoProcessUtil import GeoProcessUtil
np.seterr(divide='ignore', invalid='ignore')    # 消除 RuntimeWarning
from numpy import exp
import datetime


class IndexCalculatTools:
    """指数计算工具"""

    @staticmethod
    def CloudIdentify(in_data, band650=None, band830=None, band1200=None, fillValue=None):
        """
        去云处理
        :param in_data:
        :param band650:
        :param band830:
        :param band1200:
        :return:
        """
        # 红色波段表观反射率+近红外表观反射率>0.9
        if (type(band650) is np.ndarray) and (type(band830) is np.ndarray) and (np.median(band650) < 1):
            index1 = (band650 + band830) > 0.9
            in_data[index1] = fillValue

        if (type(band650) is np.ndarray) and (type(band830) is np.ndarray) and (np.median(band650) > 500):
            index1 = (band650 + band830) > 9000
            in_data[index1] = fillValue

        # 热红外波段（12um附近）的亮度温度<265
        if type(band1200) is np.ndarray:
            index2 = (band1200) < 265
            in_data[index2] = fillValue

        return in_data

    @staticmethod
    def NdviClaculat(bandNIR, bandR):
        """
        ndvi 指数计算
        :param bandR: 红光波段
        :param bandNIR: 近红外波段
        :return:
        """

        ndvi = (bandNIR - bandR) / (bandNIR + bandR)
        ndvi[ndvi > 1] = np.nan
        ndvi[ndvi < -1] = np.nan

        return ndvi

    @staticmethod
    def EviClaculat(bandNIR, bandR, bandB):
        """
        Evi 指数计算
        :param bandNIR: 近红外波段
        :param bandR: 红光波段
        :param bandB: 蓝光波段
        :return:
        """

        Evi = 2.5 * (bandNIR - bandR) / (bandNIR + 6 * bandR - 7.5 * bandB + 10000)
        Evi[Evi > 1] = np.nan
        Evi[Evi < -1] = np.nan

        return Evi

    @staticmethod
    def LaiClaculat(bandNIR, bandR):
        """
        Lai 指数计算
        :param bandNIR: 近红外波段
        :param bandR: 红光波段
        :return:
        """
        Ndvi = IndexCalculatTools.NdviClaculat(bandNIR, bandR)
        Lai = 2.4762 * Ndvi + 2.1245
        idx = np.where(((Ndvi != 0) & ((-1 <= Ndvi) & (Ndvi < 0.2))))
        Lai[idx] = 0.0001
        Lai[Lai > 10] = np.nan
        Lai[Lai < 0] = np.nan

        return Lai

    @staticmethod
    def VfcClaculat(bandNIR, bandR):
        """
        Vfc 指数计算
        :param bandNIR: 近红外波段
        :param bandR: 红光波段
        :return:
        """
        Ndvi = IndexCalculatTools.NdviClaculat(bandNIR, bandR)
        Vfc = (Ndvi - 0.15) / (0.9 - 0.15)

        Vfc[Vfc < 0.15] = -9999.0
        Vfc[Vfc > 0.9] = 1

        return Vfc

    @staticmethod
    def GviClaculat(inputFile, bandB, bandG, bandR, bandNIR, bandMIR1, bandMIR2):
        """
        绿度指数计算
        :param inputFile: Landsat TM数据
        :param bandB: 蓝光波段
        :param bandG: 绿光波段
        :param bandR: 红光波段
        :param bandNIR: 近红外波段
        :param bandMIR1: 中红外1波段
        :param bandMIR2: 中红外2波段
        :param scale: 数据重采样倍数
        :return:
        """
        dataB, im_width, im_height, im_bands, im_geotrans, im_proj = GeoProcessUtil.read_tiff(inputFile, bandB)
        dataB = dataB.astype('float32')
        Gvi_temp = -0.2491 * dataB
        del dataB

        dataG = GeoProcessUtil.read_tiff(inputFile, bandG)[0]
        dataG = dataG.astype('float32')
        Gvi_temp = Gvi_temp - 0.243 * dataG
        del dataG

        dataR = GeoProcessUtil.read_tiff(inputFile, bandR)[0]
        dataR = dataR.astype('float32')
        Gvi_temp = Gvi_temp - 0.5424 * dataR
        del dataR

        dataNIR = GeoProcessUtil.read_tiff(inputFile, bandNIR)[0]
        dataNIR = dataNIR.astype('float32')
        Gvi_temp = Gvi_temp + 0.7276 * dataNIR
        del dataNIR

        dataMIR1 = GeoProcessUtil.read_tiff(inputFile, bandMIR1)[0]
        dataMIR1 = dataMIR1.astype('float32')
        Gvi_temp = Gvi_temp + 0.0713 * dataMIR1
        del dataMIR1

        dataMIR2 = GeoProcessUtil.read_tiff(inputFile, bandMIR2)[0]
        dataMIR2 = dataMIR2.astype('float32')
        Gvi_temp = (Gvi_temp - 0.1608 * dataMIR2)
        Gvi_temp = np.where(Gvi_temp == 0, -9999, Gvi_temp)

        Gvi_temp[Gvi_temp < -1] = -9999

        return Gvi_temp, im_width, im_height, im_bands, im_geotrans, im_proj


    @staticmethod
    def BiomassOne(ndvi):
        """
        根据ndvi值估算生物量————一元模型
        :param ndvi:
        :return:
        """
        B = -19.704 + 630.22 * ndvi
        B[B < 0] = np.nan

        return B

    @staticmethod
    def BiomassExp(ndvi):
        """
        根据ndvi值估算生物量————指数模型
        :param ndvi:
        :return:
        """
        # B = 77.584 + np.e **(2.607 * ndvi)
        B = 83.563 + np.e **(7.647 * ndvi)
        B[B < 0] = np.nan

        return B


    @staticmethod
    def BiomassThr(ndvi):
        """
        根据ndvi值估算生物量————三次模型
        :param ndvi:
        :return:
        """
        # B = -53.548 + 1620.17 * ndvi - 4266.9 * ndvi **2 + 4742.38 * ndvi **3
        B = -53.548 + 1520.17 * ndvi - 4366.9 * ndvi **2 + 4642.38 * ndvi **3
        B[B < 0] = np.nan

        return B

    @staticmethod
    def NdwiClaculat(bandG, bandNIR):
        """
        改进水体指数
        :param bandG:
        :param baNdNIR:
        :return:
        """

        ndwi = (bandG - bandNIR) / (bandG + bandNIR)
        ndwi[ndwi > 1] = np.nan
        ndwi[ndwi < -1] = np.nan

        return ndwi

    @staticmethod
    def MNdwiClaculat(bandG, bandMIR):
        """
        改进水体指数
        :param bandG:
        :param baNdmIR:
        :return:
        """

        mndwi = (bandG - bandMIR) / (bandG + bandMIR)
        mndwi[mndwi > 1] = np.nan
        mndwi[mndwi < -1] = np.nan

        return mndwi

    @staticmethod
    def ChlaOC2(band488, band551):
        """
        叶绿素含量反演OC2算法
        :param band488: band-488反射率
        :param band551: band-551反射率
        :return:
        参考文献< 红线-数据生产和处理系统-参数产品生产模型.docx>
        """

        R2 = np.log10(band488 / band551)
        e = 0.319 - 2.336 * R2 + 0.879 * R2 ** 2 + 0.135 * R2 ** 3 - 0.071

        Cchal = 10 ** e

        Cchal[Cchal < 0.000001] = -9999
        Cchal[np.isnan(Cchal)] = -9999

        # Cchal[Cchal < 0.75] = -9999
        Cchal[Cchal > 2.5] = -9999.0
        return Cchal

    @staticmethod
    def ChlaOC3(band443, band488, band551):
        """
        叶绿素含量反演OC3算法
        :param band443:
        :param band488:
        :param band551:
        :return:
        参考文献< 红线-数据生产和处理系统-参数产品生产模型.docx>
        """
        maxR = band443
        maxR[band443 < band488] = band488[band443 < band488]

        R3 = np.log10(maxR / band551)
        e = 0.283 - 2.753 * R3 + 1.457 * R3 ** 2 + 0.659 * R3 ** 4 - 1.403 * R3 ** 4

        Cchal = 10 ** e

        Cchal[Cchal < 0.000001] = -9999
        Cchal[np.isnan(Cchal)] = -9999

        Cchal[Cchal < 0.75] = -9999
        Cchal[Cchal > 2.5] = -9999.0

        return Cchal

    @staticmethod
    def ChlaGF(band650, band830):
        """
        叶绿素a GF模型
        :param band650: b3波段
        :param band830: b4
        :return:
        """

        Cchla = 41.407 * ((band830 - band650) / (band830 + band650)) ** 2 + \
                31.283 * ((band830 - band650) / (band830 + band650)) + 13.095

        return Cchla

    @staticmethod
    def SDClaculat(band490, band555):
        """
        海水透明度反演
        :param band490:
        :param band555:
        :return:
        参考文献：《海水透明度的卫星遥感反演及其多传感器融合方法——以西北太平洋为例》
        https://max.book118.com/html/2018/0629/5314233303001300.shtm
        """

        gamma = 0.4

        band555[band555 == 0.0] = np.nan
        rate = band490 / band555
        rate[rate == 0.0] = np.nan

        SD = (0.664 + 1.772 * np.log(rate) + 0.448 * np.log(rate) ** 2) * gamma
        SD[SD < 0.00001] = -9999
        SD[np.isnan(SD)] = -9999

        SD[SD > 0.63] = -9999
        return SD

    @staticmethod
    def SDModis(band490, band555):
        """
        海水透明度反演  MODIS模型
        :param band490:
        :param band555:
        :return:
        参考文献：《海水透明度的卫星遥感反演及其多传感器融合方法——以西北太平洋为例》
        https://max.book118.com/html/2018/0629/5314233303001300.shtm
        """

        gamma = 0.4

        band555[band555 == 0.0] = np.nan
        rate = band490 / band555
        rate[rate == 0.0] = np.nan

        SD = (0.664 + 1.772 * np.log(rate) + 0.448 * np.log(rate) ** 2) * gamma
        SD[SD < 0.00001] = -9999
        SD[np.isnan(SD)] = -9999

        return SD

    @staticmethod
    def SDGF(band830):
        """
        透明度GF模型
        :param band830: b4
        :return:
        """
        TSM = 8150.8 * band830 - 2.5542
        SD = 215.4 * (TSM ** (-0.53))

        SD[SD < 0] = -9999.0
        return SD

    @staticmethod
    def SSCI(band443, band488, band531):
        """
        悬浮物浓度反演: 适用于高含沙量 > 20mg/L  MODIS 1000m分辨率
        :param band443:中心波长443的离水反射率
        :param band488:中心波长488的离水反射率
        :param band531: 中心波长531的离水反射率
        :return:
        """
        a = 0.19
        b = 0.018

        X = (band531 + band488) / band443

        SSC = exp(a + b * X)
        SSC[SSC < 0] = np.nan  # 无效值
        SSC[SSC == SSC[0][0]] = -9999  # 背景值
        SSC[np.isnan(SSC)] = -9999

        SSC[SSC > 1.29] = -9999
        SSC[SSC < 0.8] = -9999

        return SSC

    @staticmethod
    def SSCII(band413, band488):
        """
        悬浮物浓度反演: 适用于低含沙量 < 20mg/L  MODIS 1000m分辨率
        :param band413:中心波长413的离水反射率
        :param bnad488:中心波长488的离水反射率
        :return:
        """
        a = 0.19
        b = 0.018
        A = 10
        X = (band488 - band413) / A

        SSC = a + b * X
        SSC[SSC < 0] = np.nan  # 无效值
        SSC[SSC == SSC[0][0]] = -9999  # 背景值
        SSC[np.isnan(SSC)] = -9999

        return SSC

    @staticmethod
    def SSCIII(band645):
        """
        悬浮物浓度反演: MODIS 250m分辨率
        :param band645:中心波长413的离水反射率
        :return:
        """

        a = 0.19
        b = 0.018
        SSC = exp(a + b * band645)
        SSC[SSC < 0] = np.nan  # 无效值
        SSC[SSC == SSC[0][0]] = -9999  # 背景值
        SSC[np.isnan(SSC)] = -9999

        return SSC

    @staticmethod
    def TLI(chla, TP, TN, SD, CODMn):
        """利用站点数据计算TLI(湿地生态系统质量)"""
        TLIChla = 25 + 10.86 * np.log(chla)
        TLITP = 94.36 + 16.24 * np.log(TP)
        TLITN = 54.53 + 16.94 * np.log(TN)
        TLISD = 51.18 - 19.4 * np.log(SD)
        TLICOD = 1.09 + 26.6 * np.log(CODMn)

        omg = 1 + 0.7056 + 0.6742 + 0.6889 + 0.6889
        WChla = 1 / omg
        WTP = 0.7056 / omg
        WTN = 0.6742 / omg
        WSD = 0.6889 / omg
        WCODMn = 0.6889 / omg

        TLI = WChla * TLIChla + WTP * TLITP + WTN * TLITN + WSD * TLISD + WCODMn * TLICOD
        TLI[TLI > 100] = np.nan
        TLI[TLI < 0] = np.nan

        return TLI

    @staticmethod
    def TLIStation(chla, TP, TN, SD, CODMn):
        """利用站点数据计算TLI"""
        TLIChla = 25 + 10.86 * np.log(chla)
        TLITP = 94.36 + 16.24 * np.log(TP)
        TLITN = 54.53 + 16.94 * np.log(TN)
        TLISD = 51.18 - 19.4 * np.log(SD)
        TLICOD = 1.09 + 26.6 * np.log(CODMn)

        omg = 1 + 0.7056 + 0.6742 + 0.6889 + 0.6889
        WChla = 1 / omg
        WTP = 0.7056 / omg
        WTN = 0.6742 / omg
        WSD = 0.6889 / omg
        WCODMn = 0.6889 / omg

        TLI = WChla * TLIChla + WTP * TLITP + WTN * TLITN + WSD * TLISD + WCODMn * TLICOD
        TLI[TLI > 100] = -9999
        TLI[TLI < 0] = -9999

        return TLI

    @staticmethod
    def TLIRS(chla, SD):
        # 遥感法计算TLI
        TLIChla = 25 + 10.86 * np.log(chla)
        TLISD = 51.18 - 19.4 * np.log(SD)

        omg = 1 + 0.6889
        WChla = 1 / omg
        WSD = 0.6889 / omg

        TLI = WChla * TLIChla + WSD * TLISD
        TLI[TLI > 100] = -9999
        TLI[TLI < 0] = -9999

        return TLI

    @staticmethod
    def TLII(chla):
        """
        富营养化计算  单因子法——chla
        :param chla: chla浓度
        :return:
        """
        TLI = 25 + 10.86 * np.log(chla)
        TLI[TLI > 100] = np.nan
        TLI[TLI < 0] = np.nan

        return TLI

    @staticmethod
    def TLIII(sd):
        """
        富营养化计算 单因子法——SD
        :param sd: 水体透明度
        :return:
        """
        TLI = 51.18 - 19.4 * np.log(sd)
        # TLI[TLI > 100] = np.nan
        # TLI[TLI < 0] = np.nan

        return TLI

    @staticmethod
    def TLIIII(chla, SD, TP, TN):
        """
        富营养化计算 多因子法——chla, SD, TP, TN
        :param chla: 叶绿素a浓度
        :param SD: 透明度
        :param TP: 总磷
        :param TN: 总氮
        :return:
        """
        # 【1】--------------营养度计算--------------------------
        TLIChla = 25 + 10.86 * np.log(chla)
        TLISD = 51.18 - 19.4 * np.log(SD)
        TLITP = 94.36 + 16.24 * np.log(TP)
        TLITN = 54.53 + 16.94 * np.log(TN)

        # 【2】--------------权重计算-----------------------------
        omg = 1 + 0.7056 + 0.6742 + 0.6889
        WChla = 1 / omg
        WTP = 0.7056 / omg
        WTN = 0.6742 / omg
        WSD = 0.6889 / omg

        TLI = WChla * TLIChla + WTP * TLITP + WTN * TLITN + WSD * TLISD
        TLI[TLI > 100] = np.nan
        TLI[TLI < 0] = np.nan

        return TLI

    @staticmethod
    def sort_by_ID(base_array1, array2):
        data_width = base_array1.shape[0]
        data_length = array2.shape[1]
        new_array = np.zeros((data_width, data_length), dtype='float64')
        new_array[:, 0] = base_array1[:, 0]

        i = 0
        while i < data_width:
            j = 0
            while j < data_width:
                if new_array[i][0] == array2[j][0]:
                    new_array[i, 1:] = array2[j, 1:]
                j = j + 1
            i = i + 1
        return new_array

    @staticmethod
    def BriClaculat(country_value):
        """
        生境质量指数计算
        :param dataIndex: 生物多样性指数数据
        :param Area: 县行政区划的面积，单位平方千米
        :return:
        """
        data_width = country_value.shape[0]
        Bri = np.zeros((data_width, 2), dtype='float64')

        i = 0
        while i < data_width:
            Bri[i][0] = country_value[i][0]
            Bri[i][1] = 511.2642131067 * ((
                    0.35 * 0.6 * country_value[i][2] + 0.35 * 0.25 * country_value[i][3] + 0.35 * 0.15 * (
                    country_value[i][4] + country_value[i][5]) + 0.21 * 0.6 * country_value[i][6] + 0.21 * 0.3 *
                    country_value[i][7] + 0.21 * 0.1 * country_value[i][8] + 0.28 * 0.1 * country_value[i][
                        9] + 0.28 * 0.3 * (country_value[i][10] + country_value[i][11]) + 0.28 * 0.5 * (
                            country_value[i][12] + country_value[i][13]) + 0.11 * 0.6 * country_value[i][
                        15] + 0.11 * 0.4 * country_value[i][16] + 0.04 * 0.3 * country_value[i][17] + 0.04 * 0.4 *
                    country_value[i][18] + 0.04 * 0.3 * country_value[i][19] + 0.01 * 0.2 * country_value[i][
                        20] + 0.01 * 0.3 * country_value[i][21] + 0.01 * 0.2 * country_value[i][22] + 0.01 * 0.2 *
                    country_value[i][23] + 0.01 * 0.1 * country_value[i][24])) / country_value[i][1]
            i = i + 1
        return Bri

    @staticmethod
    def get_excel_WNDI(excel_file, sheet_name):
        readbook = xlrd.open_workbook(excel_file)
        sheet = readbook.sheet_by_name(sheet_name)
        need = np.array(sheet._cell_values)
        cols = sheet._dimncols
        rows = sheet._dimnrows
        data = need[1:rows + 1, 0:cols + 1].astype('float64')
        return data

    @staticmethod
    def WndiClaculat(array_area, river_data, oldwater_data, newwater_data, waterArea_data):
        """
        水网密度指数计算
        :param dataWndi: 水网密度原始数据
        :param Area: 县行政区划的面积，单位平方千米
        :return:
        """
        data_width = array_area.shape[0]
        Wndi = np.zeros((data_width, 2), dtype='float64')

        # 计算水资源量年均值
        water_mean = np.zeros((data_width, 2), dtype='float64')
        oldwater_length = oldwater_data.shape[1]
        water_mean[:, 0] = oldwater_data[:, 0]
        i = 1
        while i < oldwater_length:
            water_mean[:, 1] = water_mean[:, 1] + oldwater_data[:, i]
            i = i + 1
        water_mean[:, 1] = water_mean[:, 1] / (oldwater_length - 1)

        # 以当年数据ID为准，排序历年水资源量均值数据,计算水资源量
        water_mean_sort = IndexCalculatTools.sort_by_ID(newwater_data, water_mean)
        a_value = np.zeros((data_width, 2), dtype='float64')
        a_value[:, 0] = newwater_data[:, 0]
        a_value[:, 1] = newwater_data[:, 1] / water_mean_sort[:, 1]

        Awr_temp = np.zeros((data_width, 2), dtype='float64')
        Awr_temp[:, 0] = newwater_data[:, 0]
        Awr_temp[:, 1] = np.where(a_value[:, 1] <= 1.4, newwater_data[:, 1], 0)
        Awr_temp[:, 1] = (
            np.where(((a_value[:, 1] >= 1.4) & (a_value[:, 1] <= 2.4)), (water_mean_sort[:, 1] * (2.4 - a_value[:, 1])),
                     Awr_temp[:, 1]))

        # 计算水网密度指数
        river_data_sort = IndexCalculatTools.sort_by_ID(array_area, river_data)
        waterArea_data_sort = IndexCalculatTools.sort_by_ID(array_area, waterArea_data)
        Awr_temp_sort = IndexCalculatTools.sort_by_ID(array_area, Awr_temp)

        Wndi[:, 0] = array_area[:, 0]
        Wndi[:, 1] = ((84.3704083981 * river_data_sort[:, 1]) + (591.7908642005 * waterArea_data_sort[:, 1]) + (
                86.3869548281 * Awr_temp_sort[:, 1])) / (3 * array_area[:, 1])

        return Wndi

    @staticmethod
    def LsiClaculat(array_area, LandErosion_data, LandUse_data):
        """
        土地胁迫指数计算
        :param dataWndi: 水网密度原始数据
        :param Area: 县行政区划的面积，单位平方千米
        :return:
        """
        data_width = array_area.shape[0]
        Lsi = np.zeros((data_width, 2), dtype='float64')

        # 提取各类建筑用地面积并基于ID排序
        Build_data = np.zeros((data_width, 4), dtype='float64')
        Build_data[:, 0] = LandUse_data[:, 0]
        Build_data[:, 1:4] = LandUse_data[:, 17:20]

        Build_Area = np.zeros((data_width, 2), dtype='float64')
        Build_Area[:, 0] = Build_data[:, 0]
        Build_Area[:, 1] = (Build_data[:, 1] + Build_data[:, 2] + Build_data[:, 3])
        Build_Area_sort = IndexCalculatTools.sort_by_ID(array_area, Build_Area)

        # 土地侵蚀数据排序
        LandErosion_sort = IndexCalculatTools.sort_by_ID(array_area, LandErosion_data)

        # 计算土地胁迫指数
        Lsi[:, 0] = array_area[:, 0]
        Lsi[:, 1] = 236.04356779 * (
                    0.4 * LandErosion_sort[:, 1] + 0.2 * LandErosion_sort[:, 2] + 0.2 * Build_Area_sort[:,
                                                                                        1] + 0.2 * LandErosion_sort[:,
                                                                                                   3]) / (
                                array_area[:, 1])

        return Lsi

    @staticmethod
    def PliClaculat(array_area, Pollutant_data, water_data):
        """
        污染负荷指数计算
        :param dataPli: 土地胁迫原始数据
        :param Area: 县行政区划的面积，单位平方千米
        :return:
        """
        data_width = array_area.shape[0]
        Pli = np.zeros((data_width, 2), dtype='float64')

        # 排序污染物数据、年降水数据
        Pollutant_data_sort = IndexCalculatTools.sort_by_ID(array_area, Pollutant_data)
        water_data_sort = IndexCalculatTools.sort_by_ID(array_area, water_data)

        # 计算年总降水量
        all_water_data = np.zeros((data_width, 2), dtype='float64')
        all_water_data[:, 0] = water_data_sort[:, 0]
        all_water_data[:, 1] = water_data_sort[:, 1] * (array_area[:, 1])  # 年总降水量,单位mm*km*km

        # 计算污染负荷指数
        Pli[:, 0] = array_area[:, 0]
        Pli[:, 1] = (0.2 * 4.3937397289 * Pollutant_data_sort[:, 1] / all_water_data[:, 1]) + (
                0.2 * 40.1764754986 * Pollutant_data_sort[:, 2] / all_water_data[:, 1]) + (
                            0.2 * 0.0648660287 * Pollutant_data_sort[:, 3] / (array_area[:, 1])) + (
                            0.1 * 4.0904459321 * Pollutant_data_sort[:, 4] / (array_area[:, 1])) + (
                            0.2 * 0.5103049278 * Pollutant_data_sort[:, 5] / (array_area[:, 1])) + (
                            0.1 * 0.0749894283 * Pollutant_data_sort[:, 6] / (array_area[:, 1]))

        return Pli

    @staticmethod
    def EriClaculat(array_area, Eri_data):
        """
        环境限制指数计算
        :param Eri_data: 环境限制数据
        :param array_area: 县行政区划的ID和面积，单位平方千米
        :return:
        """
        # 排序环境限制数据
        Eri_data_sort = IndexCalculatTools.sort_by_ID(array_area, Eri_data)

        return Eri_data_sort

    @staticmethod
    def EiClaculat(array_area, Ei_data):
        """
        生态环境状况指数计算
        :param array_area: 行政区划ID和面积
        :param Ei_data: 6个分指数
        :return:
        """
        data_width = array_area.shape[0]
        Ei = np.zeros((data_width, 2), dtype='float64')
        temp_data = Ei_data[:, 2:].astype('float64')
        temp_data[:, 0:5] = np.around(temp_data[:, 0:5], decimals=1)
        temp_data[:, 5] = np.around(temp_data[:, 5], decimals=0)
        Ei_data_new = Ei_data
        Ei_data_new[:, 2:] = temp_data

        # 计算生态环境状况指数
        Ei[:, 0] = Ei_data[:, 0].astype('float64')
        Ei[:, 1] = 0.35 * temp_data[:, 0] + 0.25 * temp_data[:, 1] + 0.15 * temp_data[:, 2] + 0.15 * (
                    100 - temp_data[:, 3]) + 0.1 * (100 - temp_data[:, 4])

        # 根据环境限制指数调整生态环境状况指数
        i = 0
        while i < data_width:
            if Ei_data[i][7].astype('float64') == 2:
                if Ei[i][1] >= 75:
                    Ei[i][1] = 74.9
                elif (Ei[i][1] >= 55) and (Ei[i][1] < 75):
                    Ei[i][1] = 54.9
                elif (Ei[i][1] >= 35) and (Ei[i][1] < 55):
                    Ei[i][1] = 34.9
                elif (Ei[i][1] >= 20) and (Ei[i][1] < 35):
                    Ei[i][1] = 19.9
            elif Ei_data[i][7].astype('float64') == 3:
                if Ei[i][1] >= 75:
                    Ei[i][1] = 54.9
                elif (Ei[i][1] >= 55) and (Ei[i][1] < 75):
                    Ei[i][1] = 54.9
                elif (Ei[i][1] >= 35) and (Ei[i][1] < 55):
                    Ei[i][1] = 34.9
                elif (Ei[i][1] >= 20) and (Ei[i][1] < 35):
                    Ei[i][1] = 19.9
            i = i + 1

        # 用于shp转tif的字段值
        Ei_sort = IndexCalculatTools.sort_by_ID(array_area, Ei)

        # EI划分等级
        Ei_level = np.zeros((data_width, 2), dtype='<U9')
        Ei_level[:, 0] = Ei_data[:, 0]
        Ei_level[:, 1] = np.where(Ei[:, 1] < 20, '差', '待定')
        Ei_level[:, 1] = np.where((Ei[:, 1] >= 20) & (Ei[:, 1] < 35), '较差', Ei_level[:, 1])
        Ei_level[:, 1] = np.where((Ei[:, 1] >= 35) & (Ei[:, 1] < 55), '一般', Ei_level[:, 1])
        Ei_level[:, 1] = np.where((Ei[:, 1] >= 55) & (Ei[:, 1] < 75), '良', Ei_level[:, 1])
        Ei_level[:, 1] = np.where((Ei[:, 1] >= 75), '优', Ei_level[:, 1])

        # EI排名
        Ei_Rank = np.zeros((data_width, 2), dtype='float64')
        Ei_Rank[:, 0] = Ei[:, 0]
        Ei_argsort = np.zeros((data_width, 3), dtype='float64')
        Ei_argsort[:, 0:2] = Ei[np.argsort(-Ei[:, 1])]
        Ei_argsort[:, 2] = 1
        i1 = 1
        Rank = 1
        RTR = 1
        while i1 < data_width:
            RTR = RTR + 1
            if Ei_argsort[i1][1] != Ei_argsort[i1 - 1][1]:
                Rank = RTR
                Ei_argsort[i1][2] = Rank
            else:
                Ei_argsort[i1][2] = Rank
            i1 = i1 + 1

        i2 = 0
        while i2 < data_width:
            j2 = 0
            while j2 < data_width:
                if Ei_Rank[i2][0] == Ei_argsort[j2][0]:
                    Ei_Rank[i2][1] = Ei_argsort[j2][2]
                j2 = j2 + 1
            i2 = i2 + 1
        return Ei, Ei_sort, Ei_level, Ei_Rank, Ei_data_new

    @staticmethod
    def get_excel_EI(excel_file, sheet_name):
        readbook = xlrd.open_workbook(excel_file)
        sheet = readbook.sheet_by_name(sheet_name)
        need = np.array(sheet._cell_values)
        cols = sheet._dimncols
        rows = sheet._dimnrows
        data = need[1:rows + 1, 0:cols + 1]
        return data

    @staticmethod
    def EiWrite(Ei_data, Ei, Ei_level, Ei_Rank, excel_path):
        data_width = Ei_data.shape[0]
        Ei_info = np.zeros((data_width, 11), dtype='<U12')
        Ei_info[:, 0:8] = Ei_data
        Ei_info[:, 8] = np.around(Ei[:, 1], decimals=1)
        Ei_info[:, 9] = Ei_level[:, 1]
        Ei_info[:, 10] = Ei_Rank[:, 1].astype(np.int)

        # 写出数据到excel
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('EI', cell_overwrite_ok=True)
        # 写表头
        title = ['ID', u'行政区划名', u'生物丰度指数', u'植被覆盖度指数', u'水网密度指数', u'土地胁迫指数', u'污染负荷指数', u'环境限制指数', 'EI', u'等级', u'排名']
        jj = 0
        style = xlwt.XFStyle()
        style.alignment.horz = 2
        for line0 in title:
            worksheet.write(0, jj, line0)
            jj = jj + 1

            # 写各行政区划各类土地利用的面积
            i0 = 1
            for line1 in Ei_info:
                j0 = 0
                for line2 in line1:
                    worksheet.write(i0, j0, line2, style)
                    j0 = j0 + 1
                i0 = i0 + 1
        workbook.save(excel_path)

    @staticmethod
    def EigClaculat(inputfile):
        dataEI, im_width, im_height, im_bands, im_geotrans, im_proj = GdalBase.read_tiff(inputfile, 1)
        dataEI = dataEI.astype('float32')
        Eig = np.where(dataEI < 20, 5, 0)
        Eig = np.where((dataEI >= 20) & (dataEI < 35), 4, Eig)
        Eig = np.where((dataEI >= 35) & (dataEI < 55), 3, Eig)
        Eig = np.where((dataEI >= 55) & (dataEI < 75), 2, Eig)
        Eig = np.where(dataEI >= 75, 1, Eig)
        Eig = Eig.astype('int16')

        return Eig, im_width, im_height, im_bands, im_geotrans, im_proj

    @staticmethod
    def EicClaculat(BaseEi_file, inputFile):
        dataEI, im_width, im_height, im_bands, im_geotrans, im_proj = GdalBase.read_tiff(inputFile, 1, buf_xsize=18475,
                                                                                         buf_ysize=14550)
        dataEI = dataEI.astype('float32')

        dataBase = GdalBase.read_tiff(BaseEi_file, 1, buf_xsize=18475, buf_ysize=14550)[0]
        dataBase = dataBase.astype('float32')

        diffEi = dataEI - dataBase
        del dataEI, dataBase

        Eic = np.where(diffEi >= 8, 1, 0)
        Eic = np.where((diffEi >= 3) & (diffEi < 8), 2, Eic)
        Eic = np.where((diffEi >= 1) & (diffEi < 3), 3, Eic)
        Eic = np.where((diffEi > -1) & (diffEi < 1), 4, Eic)
        Eic = np.where((diffEi > -3) & (diffEi <= -1), 5, Eic)
        Eic = np.where((diffEi > -8) & (diffEi <= -3), 6, Eic)
        Eic = np.where(diffEi <= -8, 7, Eic)
        Eic = Eic.astype('int16')

        return Eic, im_width, im_height, im_bands, im_geotrans, im_proj

    @staticmethod
    def EifClaculat(BaseEi_file, inputFile):
        dataEI, im_width, im_height, im_bands, im_geotrans, im_proj = GdalBase.read_tiff(inputFile, 1, buf_xsize=18475,
                                                                                         buf_ysize=14550)
        dataEI = dataEI.astype('float32')

        dataBase = GdalBase.read_tiff(BaseEi_file, 1, buf_xsize=18475, buf_ysize=14550)[0]
        dataBase = dataBase.astype('float32')

        diffEi = np.abs(dataEI - dataBase)
        del dataEI, dataBase

        Eif = np.where(diffEi < 1, 1, 0)
        Eif = np.where((diffEi >= 1) & (diffEi < 3), 2, Eif)
        Eif = np.where((diffEi >= 3) & (diffEi < 8), 3, Eif)
        Eif = np.where(diffEi >= 8, 4, Eif)
        Eif = Eif.astype('int16')

        return Eif, im_width, im_height, im_bands, im_geotrans, im_proj

    @staticmethod
    def SrClaculat(inputFile, K_path, LS_path, VFC_path):
        """
        土壤保持 指数计算
        :param dataR: 气象站点降雨数据
        :param dataK: 降雨侵蚀力因子
        :param dataLS: 地形因子
        :param dataC: 植被覆盖度因子
        :return:
        """
        rainR_data, im_width, im_height, im_bands, im_geotrans, im_proj = GdalBase.read_tiff(inputFile, 1)
        rainR_data = rainR_data.astype('float32')

        K_data = GdalBase.read_tiff(K_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        K_data = K_data.astype('float32')
        Sr = rainR_data * K_data
        del rainR_data, K_data

        LS_data = GdalBase.read_tiff(LS_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        LS_data = LS_data.astype('float32')
        Sr = Sr * LS_data
        del LS_data

        VFC_data = GdalBase.read_tiff(VFC_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        VFC_data = VFC_data.astype('float32')
        Sr = Sr * (1 - VFC_data)
        del VFC_data

        return Sr, im_width, im_height, im_bands, im_geotrans, im_proj

    @staticmethod
    def WcClaculat(inputFile, RO_path, ETi_path):
        """
        水源涵养计算
        :param inputFile: 降雨数据
        :param RO_path: 地表径流数据
        :param ETi_path: 蒸散发数据
        :param Eco_path: 生态系统类型数据
        :return:
        """
        rain_data, im_width, im_height, im_bands, im_geotrans, im_proj = GdalBase.read_tiff(inputFile, 1)
        rain_data = rain_data.astype('float32')

        RO_data = GdalBase.read_tiff(RO_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        RO_data = RO_data.astype('float32')
        TQ = rain_data - RO_data
        del rain_data, RO_data

        ETi_data = GdalBase.read_tiff(ETi_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        ETi_data = ETi_data.astype('float32')
        TQ = TQ - ETi_data

        del ETi_data

        TQ = TQ * 0.9

        return TQ, im_width, im_height, im_bands, im_geotrans, im_proj

    @staticmethod
    def WbsfClaculat(WF_path, EF_path, SCF_path, K_path, C_path, z_value):
        dataWF, im_width, im_height, im_bands, im_geotrans, im_proj = GdalBase.read_tiff(WF_path, 1)
        dataWF = dataWF.astype('float32')

        dataEF = GdalBase.read_tiff(EF_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        dataEF = dataEF.astype('float32')
        data_temp = dataWF * dataEF
        del dataWF, dataEF

        dataSCF = GdalBase.read_tiff(SCF_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        dataSCF = dataSCF.astype('float32')
        data_temp = data_temp * dataSCF
        del dataSCF

        dataK = GdalBase.read_tiff(K_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        dataK = dataK.astype('float32')
        data_temp = data_temp * dataK
        del dataK

        dataC = GdalBase.read_tiff(C_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        dataC = dataC.astype('float32')
        data_temp = data_temp * dataC
        del dataC

        S = (105.71 * np.power(data_temp, -0.3711))
        Sl = (2 * z_value * 109.8 * data_temp) * np.exp(-np.power((z_value / S), 2)) / (S * S)
        del S, data_temp
        return Sl, im_width, im_height, im_bands, im_geotrans, im_proj

    @staticmethod
    def BdiClaculat(inputFile, M_rain_path, M_t_path, S_h_path):
        """
        生物多样性 指数计算
        :param inputFile: 多年植被净初级生产力平均值数据地址
        :param K_path: 降雨侵蚀力因子数据地址
        :param Fslo_path: 坡度因子数据地址
        :return:
        """
        dataNPP, im_width, im_height, im_bands, im_geotrans, im_proj = GdalBase.read_tiff(inputFile, 1)
        dataNPP = dataNPP.astype('float32')

        dataM_rain = GdalBase.read_tiff(M_rain_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        dataM_rain = dataM_rain.astype('float32')
        Spro = dataNPP * dataM_rain
        del dataNPP, dataM_rain

        dataM_t= GdalBase.read_tiff(M_t_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        dataM_t = dataM_t.astype('float32')
        Spro = Spro * dataM_t
        del dataM_t

        dataS_h = GdalBase.read_tiff(S_h_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        dataS_h = dataS_h.astype('float32')
        Spro = Spro * (1 - dataS_h)
        del dataS_h

        return Spro, im_width, im_height, im_bands, im_geotrans, im_proj

    @staticmethod
    def CeaClaculat(Cea_data, Weights_info):
        data_width = Cea_data.shape[0]
        Cea = np.zeros((data_width, 2), dtype='float64')
        Cea[:, 0] = Cea_data[:, 0]
        Cea[:, 1] = float(Weights_info[0]) * Cea_data[:, 2].astype('float64') + float(Weights_info[1]) * Cea_data[:,
                                                                                                         3].astype(
            'float64') + float(Weights_info[2]) * Cea_data[:, 4].astype('float64') + float(Weights_info[3]) * Cea_data[
                                                                                                              :,
                                                                                                              5].astype(
            'float64')

        return Cea

    @staticmethod
    def ZEUPAR(tription, chla):
        """
        计算真光层深度Zeu
        :param tription:    悬浮物浓度
        :param chla: 叶绿素a浓度
        :return:
        参考文献 《基于 VGPM 模型和 MODIS 数据估算梅梁湾浮游植物初级生产力》
        """
        zeu = 4.605 / (0.062 * tription + 0.011 * chla + 1.430)

        return zeu

    @staticmethod
    def POPT(t):
        """
        水体最大光合作用速率 PoptB
        :param t: 湖面温度
        :return:
        """
        #   -1.0 < 温度 < 28.5
        popt = 1.2956 + \
               2.749 * (10 ** -1) * t + \
               6.17 * (10 ** -2) * (t ** 2) - \
               2.05 * (10 ** -2) * (t ** 3) + \
               2.462 * (10 ** -3) * (t ** 4) - \
               1.348 * (10 ** -4) * (t ** 5) + \
               3.4132 * (10 ** -6) * (t ** 6) - \
               3.27 * (10 ** -8) * (t ** 7)

        # t <= -1.0
        popt[t <= -1.0] = 1.13

        # t >= 28.5
        popt[t >= 28.5] = 4.00

        return popt

    @staticmethod
    def DIRR(lon, lat, issue):
        """
        计算曝光时间
        :param lon: 经度
        :param lat: 维度
        :param issue: 期次
        :return:
        """
        y = int(issue[0:4])
        m = int(issue[4:6])
        d = int(issue[6:8])

        # 当前天数
        sday = datetime.date(y, m, d)
        count = sday - datetime.date(sday.year - 1, 12, 31)
        num = count.days

        # 日出时间
        risetime = (180 + 8 * 15 - lon - np.arccos(
            np.tan(10547 * np.pi / 81000 * np.cos(2 * np.pi * (num + 9) / 365)) * np.tan(
                lat * np.pi / 180)) * 180 / np.pi) / 15
        ssettime = (180 + 8 * 15 - lon + np.arccos(
            np.tan(10547 * np.pi / 81000 * np.cos(2 * np.pi * (num + 9) / 365)) * np.tan(
                lat * np.pi / 180)) * 180 / np.pi) / 15

        dirr = ssettime - risetime

        return dirr

    @staticmethod
    def FQEClaculat(inputFile, Rp_path, K_value):
        """
        森林质量评价
        :param inputFile: 基准期数据
        :param Rp_path: 评价期数据
        :param K_value: 阈值
        :return:
        """
        dataBase, im_width, im_height, im_bands, im_geotrans, im_proj = GdalBase.read_tiff(inputFile, 1)
        dataBase = dataBase.astype('float32')
        dataBase = np.where(dataBase == 0, np.nan, dataBase)

        dataRp = GdalBase.read_tiff(Rp_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        dataRp = dataRp.astype('float32')
        dataRp = np.where(dataRp == 0, np.nan, dataRp)

        dataTemp = dataRp - dataBase
        del dataBase, dataRp

        K_value = float(K_value)
        dataFqe = np.where((dataTemp > K_value) & (dataTemp > 0), 1, 0)
        dataFqe = np.where((np.abs(dataTemp) <= K_value), 2, dataFqe)
        dataFqe = np.where((np.abs(dataTemp) > K_value) & (dataTemp < 0), 3, dataFqe)

        return dataFqe, im_width, im_height, im_bands, im_geotrans, im_proj

    @staticmethod
    def GQEClaculat(inputFile, Rp_path, K_value):
        """
        草地质量评价
        :param inputFile: 基准期数据
        :param Rp_path: 评价期数据
        :param K_value: 阈值
        :return:
        """
        dataBase, im_width, im_height, im_bands, im_geotrans, im_proj = GdalBase.read_tiff(inputFile, 1)
        dataBase = dataBase.astype('float32')
        dataBase = np.where(dataBase == 0, np.nan, dataBase)


        dataRp = GdalBase.read_tiff(Rp_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        dataRp = dataRp.astype('float32')
        dataRp = np.where(dataRp == 0, np.nan, dataRp)

        dataTemp = dataRp - dataBase
        del dataBase, dataRp

        K_value = float(K_value)
        dataGqe = np.where((dataTemp > K_value) & (dataTemp > 0), 1, 0)
        dataGqe = np.where((np.abs(dataTemp) <= K_value), 2, dataGqe)
        dataGqe = np.where((np.abs(dataTemp) > K_value) & (dataTemp < 0), 3, dataGqe)

        return dataGqe, im_width, im_height, im_bands, im_geotrans, im_proj

    @staticmethod
    def REQEClaculat(inputFile, Rp_path, K_value):
        """
        区域生态系统评价
        :param inputFile: 基准期数据
        :param Rp_path: 评价期数据
        :param K_value: 阈值
        :return:
        """
        dataBase, im_width, im_height, im_bands, im_geotrans, im_proj = GdalBase.read_tiff(inputFile, 1)
        dataBase = dataBase.astype('float32')
        dataBase = np.where(dataBase == 0, np.nan, dataBase)

        dataRp = GdalBase.read_tiff(Rp_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        dataRp = dataRp.astype('float32')
        dataRp = np.where(dataRp == 0, np.nan, dataRp)

        dataTemp = dataRp - dataBase
        del dataBase, dataRp

        K_value = float(K_value)
        dataReqe = np.where((dataTemp > K_value) & (dataTemp > 0), 1, 0)
        dataReqe = np.where((np.abs(dataTemp) <= K_value), 2, dataReqe)
        dataReqe = np.where((np.abs(dataTemp) > K_value) & (dataTemp < 0), 3, dataReqe)

        return dataReqe, im_width, im_height, im_bands, im_geotrans, im_proj

    @staticmethod
    def WQEClaculat(inputFile, Rp_path, K_value):
        """
        湿地质量评价
        :param inputFile: 基准期数据
        :param Rp_path: 评价期数据
        :param K_value: 阈值
        :return:
        """
        dataBase, im_width, im_height, im_bands, im_geotrans, im_proj = GdalBase.read_tiff(inputFile, 1)
        dataBase = dataBase.astype('float32')
        dataBase = np.where(dataBase == 0, np.nan, dataBase)

        dataRp = GdalBase.read_tiff(Rp_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        dataRp = dataRp.astype('float32')
        dataRp = np.where(dataRp == 0, np.nan, dataRp)

        dataTemp = dataRp - dataBase
        del dataBase, dataRp

        K_value = float(K_value)
        dataWqe = np.where((dataTemp > K_value) & (dataTemp > 0), 1, dataTemp)
        dataWqe = np.where((np.abs(dataTemp) <= K_value), 2, dataWqe)
        dataWqe = np.where((np.abs(dataTemp) > K_value) & (dataTemp < 0), 3, dataWqe)

        return dataWqe, im_width, im_height, im_bands, im_geotrans, im_proj

    @staticmethod
    def TQEClaculat(inputFile, Rp_path, K_value):
        """
        灌丛质量评价
        :param inputFile: 基准期数据
        :param Rp_path: 评价期数据
        :param K_value: 阈值
        :return:
        """
        dataBase, im_width, im_height, im_bands, im_geotrans, im_proj = GdalBase.read_tiff(inputFile, 1)
        dataBase = dataBase.astype('float32')
        dataBase = np.where(dataBase == 0, np.nan, dataBase)

        dataRp = GdalBase.read_tiff(Rp_path, 1, buf_xsize=im_width, buf_ysize=im_height)[0]
        dataRp = dataRp.astype('float32')
        dataRp = np.where(dataRp == 0, np.nan, dataRp)

        dataTemp = dataRp - dataBase
        del dataBase, dataRp

        K_value = float(K_value)
        dataTqe = np.where((dataTemp > K_value) & (dataTemp > 0), 1, dataTemp)
        dataTqe = np.where((np.abs(dataTemp) <= K_value), 2, dataTqe)
        dataTqe = np.where((np.abs(dataTemp) > K_value) & (dataTemp < 0), 3, dataTqe)

        return dataTqe, im_width, im_height, im_bands, im_geotrans, im_proj
















