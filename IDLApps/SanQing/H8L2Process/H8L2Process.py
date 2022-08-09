# -*- coding: utf-8 -*-
'''
@File  : H8L2Process.py
@Author: admin#
@Date  : 2020/12/7 9:29
@Desc  : 
'''
import re
import os
import numpy as np
import netCDF4 as nc
from osgeo import osr
from src.common.utils.GeoProcessUtil import GeoProcessUtil


class H8L2Process:
    """H8L2级数据解析"""

    def __init__(self, inFile, productType, fillValue, tempFolder, outMark="TIF"):
        self.inFile = inFile
        self.productType = productType  # ARP/CLP/WLF
        self.fillValue = fillValue
        self.tempFolder = tempFolder
        self.outMark = outMark

        self.variables = None
        self.outFilePath = None
        self.outDataAry = None

        self.doInit()

    def doInit(self):
        if self.productType == "ARP":
            if "HARP" in self.inFile:
                self.variables = "AOT_L2_Mean"
            elif "DARP" in self.inFile:
                self.variables = "AOT_L3_Merged_Mean"
        elif self.productType == "CLP":
            self.variables = "CLTYPE"
        elif self.productType == "WLF":
            self.variables = None

    def doPrase(self, variable=None):
        """数据解析"""
        if variable is None:
            variable = self.variables

        fileName = os.path.basename(os.path.splitext(self.inFile)[0])
        self.outFilePath = self.tempFolder + "/" + fileName + "_" + self.variables + ".tif"

        try:
            nc_data_obj = nc.Dataset(self.inFile)
            data = nc_data_obj.variables[variable]
        except:
            return

        Lon = nc_data_obj.variables["longitude"][:]
        Lat = nc_data_obj.variables["latitude"][:]
        YSize = len(Lat)
        XSize = len(Lon)
        LonMin, LatMax, LonMax, LatMin = [Lon.min(), Lat.max(), Lon.max(), Lat.min()]
        Lon_Res = (LonMax - LonMin) / (float(XSize) - 1)
        Lat_Res = (LatMax - LatMin) / (float(YSize) - 1)
        geotransform = (LonMin, Lon_Res, 0, LatMax, 0, -Lat_Res)

        data = np.asarray(data)
        missing_value = nc_data_obj.variables[variable].missing_value.astype(np.float)
        idx = np.where(data == missing_value)
        data[idx] = self.fillValue

        sr = osr.SpatialReference()
        sr.ImportFromEPSG(4326)

        if self.outMark == "TIF":
            sr = osr.SpatialReference()
            sr.ImportFromEPSG(4326)
            GeoProcessUtil.write_tiff(data, XSize, YSize, 1, geotransform, sr.ExportToWkt(),
                                      self.outFilePath, self.fillValue)

            return self.outFilePath, XSize, YSize, geotransform

        elif self.outMark == "ARY":
            self.outDataAry = data

            return self.outDataAry, XSize, YSize, geotransform


if __name__ == "__main__":
    inFile = r"D:\PUUSDATA\ARP\2020-12-03\Day\H08_20201203_0000_1DARP031_FLDK.02401_02401.nc"
    productType = "ARP"
    fillValue = -1
    tempFolder = r"C:\Users\admin\Desktop"
    outMark = "TIF"
    obj = H8L2Process(inFile, productType, fillValue, tempFolder, outMark="TIF")
    outFilePath, XSize, YSize, geotransform = obj.doPrase()
