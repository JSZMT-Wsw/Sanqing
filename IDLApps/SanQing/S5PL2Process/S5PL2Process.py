# -*- coding: utf-8 -*-
'''
@File  : S5PL2Process.py
@Author: admin#
@Date  : 2020/12/1 8:43
@Desc  : 
'''

import h5py
import netCDF4 as nc
import sys
import glob
import os
import math
import numpy as np
import matplotlib as mpl

mpl.use('Agg')
from pycama import JobOrderParser, Reader, WorldPlot

from osgeo import osr
import copy
from src.common.utils.GeoProcessUtil import GeoProcessUtil


class S5PL2Process:
    """s5p-tropomi-l2-process，主要是多期拼接问题, 处理都为5km"""

    def __init__(self, issue, inputFiles, productType, model, fillValue, shpPath, tempFolder):
        """
         `` issue:期次
         ``inputFiles: 输入文件列表
         ``productType: 产品类型，NO2/SO2/O3/HCHO/CH4
         ``model: 处理方式: model=1, gdal方法拼接； model=2, pycama拼接
         ``fillValue: 更改填充值
         ``tempFolder: 临时文件
        """
        self.issue = issue
        self.inputFiles = inputFiles
        self.productType = productType
        self.model = int(model)
        self.fillValue = fillValue
        self.shpPath = shpPath
        self.tempFolder = tempFolder
        self.outFilePath = ""

        # 字段信息
        self.variables = ""
        self.longitude = "longitude"
        self.latitude = "latitude"
        self.doInit()

    def doInit(self):
        """字段信息"""
        if self.productType == "NO2":
            self.productType = "NO2___"
            self.variables = "nitrogendioxide_tropospheric_column"
        elif self.productType == "SO2":
            self.productType = "SO2___"
            self.variables = "sulfurdioxide_total_vertical_column"
        elif self.productType == "O3":
            self.productType = "O3____"
            self.variables = "ozone_total_vertical_column"
        elif self.productType == "HCHO":
            self.productType = "HCHO__"
            self.variables = "formaldehyde_tropospheric_vertical_column"
        elif self.productType == "CH4":
            self.productType = "CH4___"
            self.variables = "methane_mixing_ratio"

    def doPrase(self):
        if self.model == 1:
            self.outFilePath = self.gdal_s5p_tropomi()
        elif self.model == 2:
            self.outFilePath = self.pycamaProc_stp_tropomi()
        else:
            print("model key must input 1 or 2")
            return

        if os.path.exists(self.outFilePath):
            return self.outFilePath
        else:
            return None

    def gdal_s5p_tropomi(self):
        """model=1, gdal方法处理"""
        FillValue = None
        in_ds = []
        for nc_file in self.inputFiles.split(','):
            try:
                data = nc.Dataset(nc_file)
            except:
                continue
            prod = data.groups['PRODUCT']
            prodvar = prod.variables[self.variables][0, :, :]  # 掩码数组
            var_data = prodvar._data
            FillValue = prod.variables[self.variables]._FillValue

            idx1 = np.where(var_data == FillValue)
            idx2 = np.where(var_data < 0)

            if self.productType != "CH4___":
                var_data = var_data * 1e4
            var_data[idx1] = np.nan
            var_data[idx2] = np.nan

            #  滑动平均
            var_data_ = copy.deepcopy(var_data)
            step = 1
            for i in range(step, var_data_.shape[0] - step):
                for j in range(step, var_data_.shape[1] - step):
                    win = var_data[i - step:i + step + 1, j - step:j + step + 1]
                    nanidx = np.where(np.isnan(win))
                    if len(nanidx[0]) == 9:
                        continue
                    var_data_[i, j] = np.nanmean(var_data_[i - step:i + step + 1, j - step:j + step + 1])

            Lon = prod.variables['longitude'][0]
            Lat = prod.variables['latitude'][0]

            h5FilePath = self.tempFolder + "/" + os.path.basename(os.path.splitext(nc_file)[0]) + ".h5"
            f = h5py.File(h5FilePath, "w")
            f[self.latitude] = Lat
            f[self.longitude] = Lon
            f[self.variables] = var_data_
            f.close()

            cur_ds = GeoProcessUtil.hdf_corretion_by_vrt(h5FilePath, self.variables, FillValue, self.longitude,
                                                         self.latitude)
            in_ds.append(cur_ds)

        out_mosaic_file = self.tempFolder + "/" + self.productType + "_" + self.issue + "_mosaic.tiff"
        GeoProcessUtil.raster_mosaic(out_mosaic_file, "LAST", FillValue, self.fillValue, in_ds)

        outFilePath = self.tempFolder + "/" + self.productType + "_" + self.issue + ".tiff"
        GeoProcessUtil.clip_by_shp(out_mosaic_file, self.shpPath, outFilePath)
        return outFilePath

    def pycamaProc_stp_tropomi(self):
        """pycama方法处理"""
        inputFiles = self.inputFiles.split(",")
        if len(inputFiles) < 0:
            return

        data_folder = os.path.dirname(inputFiles[0])
        cur_folder = os.path.dirname(__file__)
        create_pycama_joborder_file = cur_folder + "/" + "create_pycama_joborder.py"
        PyCAMA_config_generator_file = cur_folder + "/" + "PyCAMA_config_generator.py"

        # 01 生成xml文件
        xml_file = glob.glob(cur_folder + "/" + "S5P_OPER_CFG_MPC_L2_*.xml")[-1]

        # 02 调用命令,生产jobFile
        exe_path = sys.executable

        Timeliness = inputFiles[0].split("_")[1]

        issue = self.issue[0:4] + "-" + self.issue[4:6] + "-" + self.issue[6:8]

        jop_file = self.tempFolder + "/" + self.issue + "_no2_jobfile"
        cmdstr = exe_path + " " + create_pycama_joborder_file + " -p " + self.productType + " -m " + Timeliness + " -c " + xml_file + " -d " + data_folder + " -D " + issue + " -o " + jop_file
        os.system(cmdstr)

        # 03 PyCAMA处理
        nc_file = self.tempFolder + "/" + self.productType + "_" + self.issue + '.nc'

        job = open(jop_file)
        joborder = JobOrderParser.JobOrder(job)
        no2reader = Reader(joborder=joborder)
        no2reader.read()
        data = WorldPlot(reader_data=no2reader, resolution=0.05)  # 分辨率控制
        data.process()
        data.dump(nc_file)

        # 提取数据
        n_target = data.n_latitude * 2
        full_data_array = np.zeros((data.n_latitude, n_target), dtype=np.float64)

        for i in range(data.latitude_centers.shape[0]):
            n = data.grid_length[i]
            ratio = n_target / n

            try:
                data_array = np.ma.asarray(data.data_for_latitude_band(i, self.variables))
                data_array.mask = (data.data_for_latitude_band(i, self.variables, count=True) == 0)
            except KeyError:
                print("Variable '{0}' could not be plotted".format(self.variables))

            if np.all(data_array.mask):
                full_data_array[i, :] = np.nan
                continue

            for j in range(n):
                start_idx = int(math.floor(ratio * j + 0.5))
                end_idx = int(math.floor(ratio * (j + 1) + 0.5))
                if data_array.mask[j]:
                    full_data_array[i, start_idx:end_idx] = np.nan
                else:
                    full_data_array[i, start_idx:end_idx] = data_array[j]
        data._full_data_array = full_data_array

        # 存储tif并裁剪
        full_data_array[full_data_array < 0] = self.fillValue
        full_data_array[np.isnan(full_data_array)] = self.fillValue
        XSize = 7200
        YSize = 3600
        geotrans = [-180, 0.05, 0, -90, 0, 0.05]
        proj = osr.SpatialReference()
        proj.ImportFromEPSG(4326)

        out_CHN_path = self.tempFolder + "/" + self.productType + "_" + self.issue + "_CHN.tif"
        ds = GeoProcessUtil.write_tiff(full_data_array, XSize, YSize, 1, geotrans, proj.ExportToWkt(), out_path=None,
                                       no_data_value=self.fillValue)
        GeoProcessUtil.clip_by_shp(ds, self.shpPath, out_CHN_path)

        # 数据平滑
        var_data, XSize, YSize, geotrans, proj = GeoProcessUtil.read_tiff(out_CHN_path, 1)
        idx = np.where(var_data == self.fillValue)
        var_data[idx] = np.nan

        if self.productType != "CH4___":
            var_data = var_data * 1e4
        var_data_ = copy.deepcopy(var_data)
        step = 1
        for i in range(step, var_data_.shape[0] - step):
            for j in range(step, var_data_.shape[1] - step):
                win = var_data[i - step:i + step + 1, j - step:j + step + 1]
                nanidx = np.where(np.isnan(win))
                if len(nanidx[0]) == 9:
                    continue
                var_data_[i, j] = np.nanmean(var_data_[i - step:i + step + 1, j - step:j + step + 1])

        outFilePath = self.tempFolder + "/" + self.productType + "_" + self.issue + ".tiff"
        GeoProcessUtil.write_tiff(var_data_, XSize, YSize, 1, geotrans, proj, out_path=outFilePath,
                                  no_data_value=self.fillValue)

        return outFilePath
