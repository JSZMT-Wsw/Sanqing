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

np.seterr(divide='ignore', invalid='ignore')  # 消除 RuntimeWarning
from numpy import exp
import datetime


class eco_monTools:
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
    def ChlaOC2(band488, band551, fillValue):
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

        Cchal[Cchal < 0.000001] = fillValue
        Cchal[np.isnan(Cchal)] = fillValue

        # Cchal[Cchal < 0.75] = fillValue
        Cchal[Cchal > 2.5] = fillValue
        return Cchal

    @staticmethod
    def ChlaOC3(band443, band488, band551, fillValue):
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

        Cchal[Cchal < 0.000001] = fillValue
        Cchal[np.isnan(Cchal)] = fillValue

        Cchal[Cchal < 0.75] = fillValue
        # Cchal[Cchal > 2.5] = fillValue

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
    def SSCI(band443, band488, band531, fillValue):
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
        SSC[SSC == SSC[0][0]] = fillValue  # 背景值
        SSC[np.isnan(SSC)] = fillValue

        SSC[SSC > 1.29] = fillValue
        SSC[SSC < 0.8] = fillValue

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
    def SDClaculat(band490, band555, fillValue):
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
        SD[SD < 0.00001] = fillValue
        SD[np.isnan(SD)] = fillValue

        # SD[SD > 0.63] = -1
        return SD



    @staticmethod
    def SDGF(band665, fillValue):
        """
        透明度GF模型
        :param band665: b4
        :return:
        """

        SD = 40 ** exp(-42.02 * band665)

        # SD[SD < 0] = fillValue
        return SD

    @staticmethod
    def SDGF2(band830, fillValue):
        """
        透明度GF模型
        :param band830: b4
        :return:
        """
        TSM = 8150.8 * band830 - 2.5542
        SD = 215.4 * (TSM ** (-0.53))

        SD[SD < 0] = fillValue
        return SD

    @staticmethod
    def TLIRS(chla, SD, fillValue):
        # 遥感法计算TLI
        TLIChla = 25 + 10.86 * np.log(chla)
        TLISD = 51.18 - 19.4 * np.log(SD)

        omg = 1 + 0.6889
        WChla = 1 / omg
        WSD = 0.6889 / omg

        TLI = WChla * TLIChla + WSD * TLISD
        TLI[TLI > 100] = fillValue
        TLI[TLI < 0] = fillValue

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
