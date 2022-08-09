# -*- coding: utf-8 -*-
'''
@File  : H8L1Process.py
@Author: admin#
@Date  : 2020/12/4 14:17
@Desc  : 
'''
import os
import numpy as np
import netCDF4 as nc
from osgeo import osr
from src.common.utils.GeoProcessUtil import GeoProcessUtil


class H8L1Process:
    """H8 L1级数据通用处理流程"""

    def __init__(self, inFile, fillValue, tempFolder, outMark="TIF"):
        """"""
        self.inFile = inFile
        self.fillValue = float(fillValue)
        self.tempFolder = tempFolder
        self.outMark = outMark  # TIF/ARY

        self.variables = {"1": "albedo_01", "2": "albedo_02", "3": "albedo_03", "4": "albedo_04", "5": "albedo_05",
                          "6": "albedo_06", "7": "tbb_07", "8": "tbb_08", "9": "tbb_09", "10": "tbb_10",
                          "11": "tbb_11", "12": "tbb_12", "13": "tbb_13", "14": "tbb_14", "15": "tbb_15",
                          "16": "tbb_16",
                          "SOZ": "SOZ", "SOA": "SOA", "SAA": "SAA", "SAZ": "SAZ"}
        self.longitude = "longitude"
        self.latitude = "latitude"
        self.SOZ = "SOZ"  # 太阳天顶角
        self.SOA = "SOA"  # 太阳方位角
        self.SAA = "SAA"  # 卫星天顶角
        self.SAZ = "SAZ"  # 卫星方位角

        self.outFilePath = ""
        self.outDataAry = ""

    def doPrase(self, bandnum):
        """数据解析"""
        bandnum = str(bandnum)

        fileName = os.path.basename(os.path.splitext(self.inFile)[0])
        self.outFilePath = self.tempFolder + "/" + fileName + "_" + self.variables[bandnum] + ".tif"

        variable = self.variables[bandnum]
        try:
            nc_data_obj = nc.Dataset(self.inFile)
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

        data = nc_data_obj.variables[variable]
        data = np.asarray(data)

        missing_value = nc_data_obj.variables[variable].missing_value.astype(np.float)
        idx = np.where(data == missing_value)

        refbds = ["1", "2", "3", "4", "5", "6"]
        if bandnum in refbds:
            data = self.getRefBand(nc_data_obj, data)

        data[idx] = self.fillValue

        if self.outMark == "TIF":
            sr = osr.SpatialReference()
            sr.ImportFromEPSG(4326)
            GeoProcessUtil.write_tiff(data, XSize, YSize, 1, geotransform, sr.ExportToWkt(),
                                      self.outFilePath, self.fillValue)

            return self.outFilePath, XSize, YSize, geotransform

        elif self.outMark == "ARY":
            self.outDataAry = data

            return self.outDataAry, XSize, YSize, geotransform

    def getRefBand(self, ds, data):
        SOZ = ds.variables['SOZ'][:].astype(np.float)  # 太阳天顶角
        SOZ[SOZ > 90] = SOZ[SOZ > 90] - 90
        ds.close()

        band = data / np.cos(SOZ * np.pi / 180)
        return band
