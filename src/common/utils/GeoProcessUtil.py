# encoding: utf-8
"""
@author: DYX
@file: GeoProcessUtil.py
@time: 2020/9/28 13:30
@desc:
"""
import re
import warnings

warnings.filterwarnings('ignore')
from pyproj import Proj
import os
import time
import xml.dom.minidom
import numpy as np
from osgeo import gdal, ogr, osr

gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
gdal.SetConfigOption("SHAPE_ENCODING", "utf-8")
ogr.RegisterAll()

from src.common.utils.FileUtil import BaseFile


class GeoProcessUtil:
    """栅格数据处理基础"""

    @staticmethod
    def read_tiff(path, idx_band, scale=None, buf_xsize=None, buf_ysize=None):
        """
        读取 TIFF 文件
        :param path: str，unicode，dataset
        :param idx_band: str，unicode，int
        :param scale: 重采样系数     # 已知原数据分辨率
        :param buf_xsize: 重采样列数     # 已知目标数据的行列
        :param buf_ysize:重采样行数
        :return:
        """

        # 参数类型检查
        if isinstance(path, gdal.Dataset):
            dataset = path
        else:
            dataset = gdal.Open(path)

        if dataset:
            XSize = dataset.RasterXSize  # 栅格矩阵的列数
            YSize = dataset.RasterYSize  # 栅格矩阵的行数
            bands = dataset.RasterCount  # 波段数
            proj = dataset.GetProjection()  # 获取投影信息
            geotrans = list(dataset.GetGeoTransform())  # 获取仿射矩阵信息

            if not (scale) is None:
                scale = float(scale)
            if not (buf_xsize) is None:
                buf_xsize = int(buf_xsize)
            if not (buf_ysize) is None:
                buf_ysize = int(buf_ysize)

            if not (scale) is None and (buf_xsize is None and buf_ysize is None):
                XSize = int(XSize * scale)
                YSize = int(YSize * scale)
                geotrans[1] = geotrans[1] / scale
                geotrans[5] = geotrans[5] / scale
            elif not (buf_xsize) is None and not (buf_ysize) is None and scale is None:
                geotrans[1] = geotrans[1] / (buf_xsize / XSize)
                geotrans[5] = geotrans[5] / (buf_ysize / YSize)
                XSize = buf_xsize
                YSize = buf_ysize

            idx_band = int(idx_band)
            if idx_band <= bands:
                in_band = dataset.GetRasterBand(idx_band)
                data = in_band.ReadAsArray(0, 0, buf_xsize=XSize, buf_ysize=YSize)  # 获取数据
                # print('read tiff success')
                return data, XSize, YSize, geotrans, proj
            else:
                print('error in read tiff')
        else:
            print('error in read tiff')

    @staticmethod
    def write_tiff(data, XSize, YSize, bands, geotrans, proj, out_path=None, no_data_value=None):
        """
        写dataset（需要一个更好的名字）
        :param data: 输入的矩阵
        :param width: 宽
        :param height: 高
        :param bands: 波段数
        :param geotrans: 仿射矩阵
        :param proj: 坐标系
        :param out_path: 输出路径，str，None
        :param no_data_value: 无效值 ；num_list ，num
        :param return_mode: TIFF : 保存为本地文件， MEMORY：保存为缓存
        :return: 当保存为缓存的时候，输出为 dataset
        """

        # 保存类型选择
        if 'int8' in data.dtype.name or 'bool' in data.dtype.name:
            datatype = gdal.GDT_Byte
        elif 'int16' in data.dtype.name:
            datatype = gdal.GDT_UInt16
        else:
            datatype = gdal.GDT_Float32
        # 矩阵波段识别
        if len(data.shape) == 3:
            bands, YSize, XSize = data.shape
        elif len(data.shape) == 2:
            # 统一处理为三维矩阵
            data = np.array([data], dtype=data.dtype)
        else:
            bands, (YSize, XSize) = 1, data.shape
        # 根据存储类型的不同，获取不同的驱动
        if out_path:
            dataset = gdal.GetDriverByName('GTiff').Create(out_path, XSize, YSize, bands, datatype)
        else:
            dataset = gdal.GetDriverByName('MEM').Create('', XSize, YSize, bands, datatype)
        # 写入数据
        if dataset is not None:
            dataset.SetGeoTransform(geotrans)
            dataset.SetProjection(proj)
        # 写入矩阵
        for i in range(bands):
            dataset.GetRasterBand(i + 1).WriteArray(data[i])
            # 写入无效值
            if no_data_value is not None:
                # 当每个图层有一个无效值的时候
                if isinstance(no_data_value, list) or isinstance(no_data_value, tuple):
                    if no_data_value[i] is not None:
                        dataset.GetRasterBand(i + 1).SetNoDataValue(no_data_value[i])
                else:
                    dataset.GetRasterBand(i + 1).SetNoDataValue(no_data_value)
        # 根据返回类型的不同，返回不同的值
        if out_path is None:
            return dataset
        else:
            del dataset

    @staticmethod
    def clip_by_shp(in_raster_file, shp_file, out_raster_file=""):
        """
        矢量裁剪栅格(矢量外边界)
        :param in_raster_file: string  in put shp file
        :param shp_file:
        :param out_raster_file:
        :return:
        """
        try:
            # 参数类型检查
            if isinstance(in_raster_file, gdal.Dataset):
                ds_raster = in_raster_file
            else:
                ds_raster = gdal.Open(in_raster_file)

            # ds_raster = gdal.Open(in_raster_file)

            ds_shp = ogr.Open(shp_file)
            layer = ds_shp.GetLayer()
            extent = layer.GetExtent()  # 西，东，南，北
            output_bounds_args = (extent[0], extent[2], extent[1], extent[3])

            if out_raster_file == "" or out_raster_file is None:
                format = "MEM"
            else:
                format = "GTiff"

                dirOut = os.path.dirname(out_raster_file)
                if BaseFile.isFileOrDir(dirOut) != BaseFile.ISDIR:
                    BaseFile.creatDir(dirOut)

            ds = gdal.Warp(out_raster_file, ds_raster, format=format,
                           cutlineDSName=shp_file, outputBounds=output_bounds_args)

            ds_shp.Destroy()
            del ds_raster

            if out_raster_file == "" or out_raster_file is None:
                return ds
            else:
                return out_raster_file
        except:
            return

    @staticmethod
    def raster_coordinaterans_by_tool(in_raster_file, dst_srs, out_raster_file=""):
        """
        栅格数据坐标系转换
        :param in_raster_file:
        :param out_raster_file:
        :param dst_srs: dst_srs = osr.SpatialReference()    dst_srs.ImportFromEPSG(102025)
        或proj = Proj('+proj=aea +lon_0=105 +lat_1=25 +lat_2=47 +ellps=krass')  dst_srs.ImportFromProj4(proj.srs)
        :return:
        """

        ds = gdal.Open(in_raster_file)
        srcNodata = ds.GetRasterBand(1).GetNoDataValue()
        if srcNodata is None:
            dstNodata = 0
        else:
            dstNodata = srcNodata

        sp = ds.GetProjection()

        src_srs = osr.SpatialReference()
        src_srs.ImportFromWkt(sp)
        src_srs_WKID = src_srs.GetAttrValue('AUTHORITY', 1)
        # print("源文件坐标系{0}".format(src_srs_WKID))

        dst_srs_WKID = dst_srs.GetAttrValue('AUTHORITY', 1)
        # print("目标文件坐标系{0}".format(dst_srs_WKID))

        if out_raster_file == "" or out_raster_file is None:
            format = "MEM"
        else:
            format = "GTiff"

            dirOut = os.path.dirname(out_raster_file)
            if BaseFile.isFileOrDir(dirOut) != BaseFile.ISDIR:
                BaseFile.creatDir(dirOut)

        out_ds = gdal.Warp(out_raster_file, ds, format=format, dstSRS=dst_srs.ExportToWkt(),
                           # resampleAlg=gdal.GRIORA_Bilinear,
                           srcNodata=dstNodata, dstNodata=dstNodata)

        del ds
        if out_raster_file == "" or out_raster_file is None:
            return out_ds
        else:
            return out_raster_file

    @staticmethod
    def vector_coordinaterans_by_tool(in_shp_file, dst_srs, out_shp_file):
        """

        :param in_shp_file:
        :param out_shp_file:
        :param dst_srs:
        :return:
        """
        ds = ogr.Open(in_shp_file)
        layer = ds.GetLayer()
        sp = layer.GetSpatialRef()
        wkt = sp.ExportToWkt()

        src_srs = osr.SpatialReference()
        src_srs.ImportFromWkt(wkt)  # wkt 格式
        src_srs_WKID = src_srs.GetAttrValue('AUTHORITY', 1)  # EPSG格式
        # print "源文件坐标系{0}".format(src_srs_WKID)

        dst_srs_WKID = dst_srs.GetAttrValue('AUTHORITY', 1)
        # print "目标文件坐标系{0}".format(dst_srs_WKID)

        gdal.VectorTranslate(out_shp_file, in_shp_file, dstSRS=dst_srs.ExportToWkt(), reproject=True)
        ds.Destroy()
        return out_shp_file

    @staticmethod
    def SpatialGeometry(rasterPath, shpMap, fillValue):
        """空间关系--主要用来判断栅格是否覆盖某一行政区划"""

        areaIDList = []

        if shpMap is None or len(shpMap) == 0:
            return None

        dsTif = gdal.Open(rasterPath)
        srcNodata = dsTif.GetRasterBand(1).GetNoDataValue()

        for shpMark in shpMap.keys():

            shpPath = shpMap[shpMark]
            if BaseFile.isFileOrDir(shpPath) != BaseFile.ISFILE:
                continue

            dsShp = ogr.Open(shpPath)
            layer = dsShp.GetLayer()
            feature = layer.GetNextFeature()
            while feature:
                curID = str(feature.GetField("ID"))

                cutline_where_args = "ID" + " = " + "\'" + curID + "\'"  # filter continue

                geom = feature.GetGeometryRef()
                envelope = geom.GetEnvelope()
                output_bounds_args = (envelope[0], envelope[2], envelope[1], envelope[3])  # feature envelope

                tmpDS = gdal.Warp("", dsTif, format="MEM", cutlineDSName=shpPath,
                                  srcNodata=srcNodata, dstNodata=srcNodata,
                                  cutlineWhere=cutline_where_args, outputBounds=output_bounds_args)

                band = tmpDS.GetRasterBand(1)
                # (minV, maxV) = band.ComputeRasterMinMax() # 注该方法在栅格和矢量不相交的情况下会抛出错误，但无影响程序执行
                minV = np.nanmin(band.ReadAsArray())
                maxV = np.nanmax(band.ReadAsArray())
                if minV == fillValue and maxV == fillValue:
                    feature = layer.GetNextFeature()
                    continue

                areaIDList.append(curID)
                del tmpDS
                feature = layer.GetNextFeature()

            dsShp.Destroy()

        del dsTif
        return areaIDList

    @staticmethod
    def NormalStastic(rasterPath, shpMap, staAry, fillValue):
        """
        统计信息入库 rasterPath-栅格文件 shpMap-行政区划字典 staAry-统计条件列表
        返回数据结构为 [AreID] = [] 数据从索引1处与统计条件一致
        """

        if shpMap is None or len(shpMap) == 0:
            return None

        dsTif = gdal.Open(rasterPath)
        srcNodata = dsTif.GetRasterBand(1).GetNoDataValue()

        staConAry = []
        for conStr in staAry:
            staConAry.append(conStr)

        dataLists = {}

        for shpMark in shpMap.keys():

            shpPath = shpMap[shpMark]
            if BaseFile.isFileOrDir(shpPath) != BaseFile.ISFILE:
                continue

            dsShp = ogr.Open(shpPath)
            layer = dsShp.GetLayer()
            feature = layer.GetNextFeature()

            while feature:
                curID = str(feature.GetField("ID"))

                cutline_where_args = "ID" + " = " + "\'" + curID + "\'"  # filter continue

                geom = feature.GetGeometryRef()
                envelope = geom.GetEnvelope()
                output_bounds_args = (envelope[0], envelope[2], envelope[1], envelope[3])  # feature envelope

                tmpDS = gdal.Warp("", dsTif, format="MEM", cutlineDSName=shpPath,
                                  srcNodata=srcNodata, dstNodata=srcNodata,
                                  cutlineWhere=cutline_where_args, outputBounds=output_bounds_args)

                band = tmpDS.GetRasterBand(1)
                # (minV, maxV) = band.ComputeRasterMinMax() # 注该方法在栅格和矢量不相交的情况下会抛出错误，但无影响程序执行
                minV = np.nanmin(band.ReadAsArray())  # 此处的最小值包含计算的无效值
                maxV = np.nanmax(band.ReadAsArray())
                if minV == fillValue and maxV == fillValue:
                    feature = layer.GetNextFeature()
                    continue

                data = GeoProcessUtil.read_tiff(tmpDS, 1)[0]
                data = data.astype(float)
                # idx = np.where((data >= minV) & (data <= maxV))
                idx = np.where(data != fillValue)
                # count = len(idx[0])
                # mean = np.nansum(data[idx]) / count
                mean = np.nanmean(data[idx])
                maxV = np.nanmax(data[idx])
                minV = np.nanmin(data[idx])

                tmpCond = ["MAX", "MEAN", "MIN"]
                tmpVal = [maxV, mean, minV]
                tmpDict = dict(zip(tmpCond, tmpVal))

                line = []
                for cursta in staAry:
                    line.append(tmpDict[cursta])
                dataLists[curID] = line

                del tmpDS
                feature = layer.GetNextFeature()

            dsShp.Destroy()

        del dsTif

        return dataLists

    @staticmethod
    def GradationStastic(outDir, rasterPath, shpMap, valueStr):
        """
        分级统计
        返回数据结构为 [AreID] = [] 数据从索引1处与统计条件一致
        """

        if shpMap is None or len(shpMap) == 0:
            return None

        t = time.time()
        milsecondStr = str(int(round(t * 1000)))  # 当前时间毫秒数
        outDirTemp = os.path.join(outDir, milsecondStr)
        BaseFile.creatDir(outDirTemp)

        minV = float(valueStr.split(" ")[2])
        maxV = float(valueStr.split(" ")[6])

        # 转投影
        fileAry = BaseFile.getFilePathInfo(rasterPath, True)

        dst_srs = osr.SpatialReference()
        proj = Proj('+proj=aea +lon_0=105 +lat_1=25 +lat_2=47 +ellps=krass')
        dst_srs.ImportFromProj4(proj.srs)

        ProjRasterPath = outDirTemp + "/" + fileAry[1] + "_Proj" + fileAry[2]
        GeoProcessUtil.raster_coordinaterans_by_tool(rasterPath, dst_srs, ProjRasterPath)
        if BaseFile.isFileOrDir(ProjRasterPath) != BaseFile.ISFILE:
            return None

        # 信息计算
        dsTif = gdal.Open(ProjRasterPath)
        srcNodata = dsTif.GetRasterBand(1).GetNoDataValue()

        # 统计
        dataLists = {}

        for shpMark in shpMap.keys():

            shpPath = shpMap[shpMark]
            if BaseFile.isFileOrDir(shpPath) != BaseFile.ISFILE:
                continue

            fileAry = BaseFile.getFilePathInfo(shpPath, True)
            ProjShpPath = outDirTemp + "/" + fileAry[1] + "_Proj" + fileAry[2]
            GeoProcessUtil.vector_coordinaterans_by_tool(shpPath, dst_srs, ProjShpPath)
            if BaseFile.isFileOrDir(ProjShpPath) != BaseFile.ISFILE:
                return

            dsShp = ogr.Open(ProjShpPath)
            layer = dsShp.GetLayer()
            feature = layer.GetNextFeature()

            while feature:
                curID = str(feature.GetField("ID"))

                cutline_where_args = "ID" + " = " + "\'" + curID + "\'"  # filter continue

                geom = feature.GetGeometryRef()
                envelope = geom.GetEnvelope()
                output_bounds_args = (envelope[0], envelope[2], envelope[1], envelope[3])  # feature envelope

                tmpDS = gdal.Warp("", dsTif, format="MEM", cutlineDSName=shpPath,
                                  srcNodata=srcNodata, dstNodata=srcNodata,
                                  cutlineWhere=cutline_where_args, outputBounds=output_bounds_args)

                data = GeoProcessUtil.read_tiff(tmpDS, 1)[0]
                geotransform = tmpDS.GetGeoTransform()
                pixArea = abs(geotransform[1] * geotransform[5]) / 1000000

                idx = np.where((data >= minV) & (data < maxV))
                count = len(idx[0])
                curArea = pixArea * count
                dataLists[curID] = (curID, round(curArea, 4))

                del tmpDS
                feature = layer.GetNextFeature()

            dsShp.Destroy()

        del dsTif

        BaseFile.removeDir(outDirTemp)
        return dataLists

    @staticmethod
    def raster_mosaic(out_raster_file, mosaic_type, srcNodata, dstNodata, args):
        """
        栅格数据镶嵌
        :param out_raster_file:
        :param mosaic_type: str UPPER， FIRST, LAST， MEAN， MINIMUM， MAXIMUM， SUM   重叠区域处理方式
        :param srcNodata:
        :param dstNodata: 多于三个tif时，应使得dstNodata == srcNodata
        :param args: str 待拼接的文件路径，任意多个
        :return:
        """
        if len(args) < 1:
            return

        if mosaic_type == "FIRST":
            in_raster_files = list(args)
            in_raster_files.reverse()
            gdal.Warp(out_raster_file, in_raster_files, format="GTiff", srcNodata=srcNodata, dstNodata=dstNodata)

        elif mosaic_type == "LAST":
            gdal.Warp(out_raster_file, list(args), format="GTiff", srcNodata=srcNodata, dstNodata=dstNodata)

        elif mosaic_type == "MEAN" or mosaic_type == "MINIMUM" or mosaic_type == "MAXIMUM" or mosaic_type == "SUM":
            if len(args) == 1:
                gdal.Warp(out_raster_file, list(args), format="GTiff", srcNodata=srcNodata, dstNodata=dstNodata)
            else:
                ds = GeoProcessUtil.mosaic_func(args[0], args[1], srcNodata, dstNodata, mosaic_type)
                for cur_raster_file in args[2:]:
                    ds = GeoProcessUtil.mosaic_func(ds, cur_raster_file, srcNodata, dstNodata, mosaic_type)
                gdal.Warp(out_raster_file, ds, format="GTiff")
                del ds
        return out_raster_file

    @staticmethod
    def mosaic_func(in_raster_file1, in_raster_file2, srcNodata, dstNodata, mosaic_type):
        """
        拼接工具函数
        :param in_raster_file1:
        :param in_raster_file2:
        :param srcNodata:
        :param dstNodata:
        :param type:
        :return:
        """
        temp_ds_befor = gdal.Warp("", [in_raster_file1, in_raster_file2], format="MEM", srcNodata=srcNodata,
                                  dstNodata=dstNodata)
        temp_ds_after = gdal.Warp("", [in_raster_file2, in_raster_file1], format="MEM", srcNodata=srcNodata,
                                  dstNodata=dstNodata)

        data_befor, XSize, YSize, geotrans, proj = GeoProcessUtil.read_tiff(temp_ds_befor, 1)
        data_after = GeoProcessUtil.read_tiff(temp_ds_after, 1)[0]
        data = np.dstack([data_befor, data_after])

        nodata_idx = np.where((data_befor == srcNodata) & (data_after == srcNodata))  # 两个影像都为无效值的索引

        out_data = None
        data[data == srcNodata] = 0  # 无效值区域赋值为0，避免出现无效值参与计算
        if mosaic_type == "MEAN":
            out_data = data.mean(axis=2)
        elif mosaic_type == "MINIMUM":
            out_data = data.min(axis=2)
        elif mosaic_type == "MAXIMUM":
            out_data = data.max(axis=2)
        elif mosaic_type == "SUM":
            out_data = data.sum(axis=2)
        out_data[nodata_idx] = dstNodata

        out_ds = GeoProcessUtil.write_tiff(out_data, XSize, YSize, 1, geotrans, proj, no_data_value=dstNodata)

        del temp_ds_befor, temp_ds_after
        del data_befor, data_after, out_data
        return out_ds

    @staticmethod
    def interpolation_by_points(in_file, z_field, shp_file, tempFolder, out_raster_file=None, cellsize=0.0025,
                                interpolation_type="invdistnn"):
        """
        :param in_file: .csv  /  .shp
        :param z_field:
        :param shp_file:
        :param tempFolder:
        :param out_raster_file:
        :param cellsize:
        :param interpolation_type:
        :return:
        """
        file_name = os.path.basename(in_file).split(".")[0]

        if os.path.splitext(in_file)[1] == ".csv":
            vrt_file = tempFolder + "/" + file_name + ".vrt"
            vrt_file = GeoProcessUtil.write_vrt(in_file, z_field, vrt_file)  # write vrt file
            srcDS = vrt_file
        elif os.path.splitext(in_file)[1] == ".shp":
            srcDS = in_file
        else:
            print("input file is not support")
            return

        ds_shp = ogr.Open(shp_file)
        extent = ds_shp.GetLayer(0).GetExtent()  # min_x, max_x, min_y, max_y
        minX = int(extent[0])
        maxX = int(extent[1]) + 1
        minY = int(extent[2])
        maxY = int(extent[3]) + 1

        nXSize = int((maxX - minX) / cellsize)
        nYSize = int((maxY - minY) / cellsize)  # set cellsize

        algorithm_args = None  # get interpolation mothed
        if interpolation_type == "invdist":
            # algorithm_args = "invdist:power=2.0:smoothing=0.0:radius1=0.0:radius2=0.0:angle=0.0:max_points=0:min_points=0:nodata=0.0"
            algorithm_args = "invdist:nodata=0.0"
        elif interpolation_type == "invdistnn":
            algorithm_args = 'invdistnn:power=2.0:smothing=0.0:radius=1.0:max_points=12:min_points=0:nodata=0.0'
        elif interpolation_type == "average":
            algorithm_args = "average:nodata=0.0"
        elif interpolation_type == "nearest":
            algorithm_args = "nearest:nodata=0.0"
        elif interpolation_type == "linear":
            algorithm_args = "linear:nodata=0.0"

        options = gdal.GridOptions(format="GTiff", outputType=gdal.GDT_Float32, width=nXSize, height=nYSize,
                                   outputBounds=(minX, minY, maxX, maxY),
                                   zfield=z_field,
                                   algorithm=algorithm_args)

        interpolation_file = tempFolder + "/" + file_name + "_interpolation.tif"
        gdal.Grid(destName=interpolation_file, srcDS=srcDS, options=options)  # interpolation process

        if out_raster_file is None:
            file_ary = os.path.splitext(in_file)
            out_raster_file = file_ary[0] + "_interpol.tif"
        out_raster_file = GeoProcessUtil.clip_by_shp(interpolation_file, shp_file, out_raster_file)

        return out_raster_file

    @staticmethod
    def write_vrt(in_csv_file, z_filed, out_vrt_file):
        """

        :param in_csv_file:
        :param z_filed:
        :param out_vrt_file:
        :return:
        """

        layer_name = os.path.basename(in_csv_file).split(".")[0]
        with open(out_vrt_file, "w") as file_write:
            file_write.write('<OGRVRTDataSource>\n')
            file_write.write('\t<OGRVRTLayer name="%s">\n' % layer_name)
            file_write.write('\t\t<SrcDataSource>%s</SrcDataSource>\n' % in_csv_file)
            file_write.write('\t\t<SrcLayer>%s</SrcLayer>\n' % layer_name)
            file_write.write('\t\t<GeometryType>wkbPoint</GeometryType>\n')
            file_write.write('\t\t\t<LayerSRS>WGS84</LayerSRS>\n')
            file_write.write(
                '\t\t<GeometryField encoding="PointFromColumns" x="LONGITUDE" y="LATITUDE" z="%s"/>\n' % z_filed)
            file_write.write('\t</OGRVRTLayer>\n')
            file_write.write('</OGRVRTDataSource>\n')

        return out_vrt_file

    @staticmethod
    def get_dataset_idx(in_file, dataset_name):
        """
        获取hdf特定子数据集的索引
        :param in_file:
        :param dataset_name:
        :return:
        """
        ds = gdal.Open(in_file)
        subdatasets = ds.GetSubDatasets()
        count = 0
        for item, sub in enumerate(subdatasets):
            # print(sub[0])
            # print(re.split(r'[:|//|\t|,]', sub[0].strip())[-1])  # 字符串以",", "//", "\t" ":" 分割
            if re.split('[:|//|\t|,]', sub[0])[-1] == dataset_name:
                break
            else:
                count += 1
        del ds, subdatasets

        if count != item: return

        return count

    @staticmethod
    def hdf_correction_by_geoloc(in_hdf_file, dataset_name, out_raster_file=None, fill_value=None):
        """
        :param in_hdf_file:
        :param dataset_name:
        :param out_raster_file:
        :return:
        """

        count = GeoProcessUtil.get_dataset_idx(in_hdf_file, dataset_name)

        ds = gdal.Open(in_hdf_file)
        subdatasets = ds.GetSubDatasets()
        sub_ds = gdal.Open(subdatasets[count][0])  # 1. get sub dataset

        p = sub_ds.RasterCount
        data_type = sub_ds.GetRasterBand(1).DataType  # 2. get args
        if fill_value is None:
            fill_value = sub_ds.GetRasterBand(1).GetNoDataValue()
        else:
            fill_value = sub_ds.GetMetadata()["_FillValue"]

        sr = osr.SpatialReference()
        sr.ImportFromEPSG(4326)

        if out_raster_file is None:
            out_raster_file_args = ""
            format_args = "MEM"
        else:
            out_raster_file_args = out_raster_file
            format_args = "GTiff"

        out_ds = gdal.Warp(out_raster_file_args, sub_ds, format=format_args, dstSRS=sr.ExportToWkt(),
                           srcNodata=fill_value, dstNodata=fill_value,
                           resampleAlg=gdal.GRIORA_Bilinear,
                           outputType=data_type)
        del ds, sub_ds

        if out_raster_file is None:
            return out_ds
        else:
            return out_raster_file

    @staticmethod
    def hdf_corretion_by_vrt(in_hdf_file, dataset_name, fill_value, lon_key, lat_key, out_raster_file=None):
        """
        :param in_hdf_file:
        :param dataset_name:
        :param fill_value:
        :param lon_key:
        :param lat_key:
        :param out_raster_file:
        :return:
        """
        count = GeoProcessUtil.get_dataset_idx(in_hdf_file, dataset_name)

        ds = gdal.Open(in_hdf_file)
        subdatasets = ds.GetSubDatasets()
        sub_ds = gdal.Open(subdatasets[count][0])

        file_ary = os.path.splitext(in_hdf_file)
        vrt_file = file_ary[0] + ".vrt"
        gdal.Translate(vrt_file, sub_ds, format="VRT")

        sr = osr.SpatialReference()
        sr.ImportFromEPSG(4326)  # 添加空间参考

        lonDS = subdatasets[GeoProcessUtil.get_dataset_idx(in_hdf_file, lon_key)][0]
        latDS = subdatasets[GeoProcessUtil.get_dataset_idx(in_hdf_file, lat_key)][0]

        # data mate / lon mate   for example: modis data is 2030x1354, but lon and lat is 406x271, 5times
        line_step = int(sub_ds.RasterXSize / gdal.Open(lonDS).RasterXSize)
        pixel_step = int(sub_ds.RasterYSize / gdal.Open(latDS).RasterYSize)

        GeoProcessUtil.update_vrt(vrt_file, sr.ExportToWkt(), lonDS, latDS, line_step, pixel_step)

        if out_raster_file is None:
            out_raster_file_args = ""
            format_args = "MEM"
        else:
            out_raster_file_args = out_raster_file
            format_args = "GTiff"

        out_ds = gdal.Warp(out_raster_file_args, vrt_file, format=format_args, dstSRS=sr.ExportToWkt(),
                           dstNodata=fill_value, geoloc=True)

        del ds, sub_ds

        if out_raster_file is None:
            return out_ds
        else:
            return out_raster_file

    @staticmethod
    def update_vrt(vrt_file, srs, X_DATASET, Y_DATASET, LINE_STEP, PIXEL_STEP):
        """
        VRT校正一定要有的信息
        <Metadata domain="GEOLOCATION">
            <MDI key="SRS">GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9108"]],AXIS["Lat",NORTH],AXIS["Long",EAST],AUTHORITY["EPSG","4326"]]</MDI>
            <MDI key="X_DATASET">HDF5:"C:\\Users\\EDZ\\Desktop\\BEI_FY3B_VIRR_20150119_062500_R005KM_CLA_NUL_NUL_L2.hdf"://Longitude</MDI>
            <MDI key="X_BAND">1</MDI>
            <MDI key="PIXEL_OFFSET">0</MDI>
            <MDI key="PIXEL_STEP">1</MDI>   # 列步长
            <MDI key="Y_DATASET">HDF5:"C:\\Users\\EDZ\\Desktop\\BEI_FY3B_VIRR_20150119_062500_R005KM_CLA_NUL_NUL_L2.hdf"://Latitude</MDI>
            <MDI key="Y_BAND">1</MDI>
            <MDI key="LINE_OFFSET">0</MDI>
            <MDI key="LINE_STEP">1</MDI>    # 行步长
        </Metadata>
        :param vrt_file:
        :param sr:
        :param X_DATASET:
        :param Y_DATASET:
        :return:
        """

        domTree = xml.dom.minidom.parse(vrt_file)
        rootNode = domTree.documentElement

        childnode = domTree.createElement("Metadata")
        childnode.setAttribute("domain", "GEOLOCATION")

        schildnode = domTree.createElement("MDI")  # SRS属性
        schildnode.setAttribute("key", "SRS")
        schildnodetext = domTree.createTextNode(srs)
        schildnode.appendChild(schildnodetext)
        childnode.appendChild(schildnode)

        schildnode = domTree.createElement("MDI")  # X_DATASET
        schildnode.setAttribute("key", "X_DATASET")
        schildnodetext = domTree.createTextNode(X_DATASET)
        schildnode.appendChild(schildnodetext)
        childnode.appendChild(schildnode)

        schildnode = domTree.createElement("MDI")  # X_BAND
        schildnode.setAttribute("key", "X_BAND")
        schildnodetext = domTree.createTextNode("1")
        schildnode.appendChild(schildnodetext)
        childnode.appendChild(schildnode)

        schildnode = domTree.createElement("MDI")  # PIXEL_OFFSET
        schildnode.setAttribute("key", "PIXEL_OFFSET")
        schildnodetext = domTree.createTextNode("0")
        schildnode.appendChild(schildnodetext)
        childnode.appendChild(schildnode)

        schildnode = domTree.createElement("MDI")  # PIXEL_STEP
        schildnode.setAttribute("key", "PIXEL_STEP")
        schildnodetext = domTree.createTextNode(str(PIXEL_STEP))
        schildnode.appendChild(schildnodetext)
        childnode.appendChild(schildnode)

        schildnode = domTree.createElement("MDI")  # Y_DATASET
        schildnode.setAttribute("key", "Y_DATASET")
        schildnodetext = domTree.createTextNode(Y_DATASET)
        schildnode.appendChild(schildnodetext)
        childnode.appendChild(schildnode)

        schildnode = domTree.createElement("MDI")  # Y_BAND
        schildnode.setAttribute("key", "Y_BAND")
        schildnodetext = domTree.createTextNode("1")
        schildnode.appendChild(schildnodetext)
        childnode.appendChild(schildnode)

        schildnode = domTree.createElement("MDI")  # LINE_OFFSET
        schildnode.setAttribute("key", "LINE_OFFSET")
        schildnodetext = domTree.createTextNode("0")
        schildnode.appendChild(schildnodetext)
        childnode.appendChild(schildnode)

        schildnode = domTree.createElement("MDI")  # LINE_STEP
        schildnode.setAttribute("key", "LINE_STEP")
        schildnodetext = domTree.createTextNode(str(LINE_STEP))
        schildnode.appendChild(schildnodetext)
        childnode.appendChild(schildnode)

        rootNode.appendChild(childnode)

        try:
            with open(vrt_file, "w") as fw:
                domTree.writexml(fw, indent='', addindent='\t', newl='\n')
        except Exception as err:
            print('错误信息：{}'.format(err))

    @staticmethod
    def raster_compose(in_raster_files, out_raster_file, fill_value=None, model="MEAN"):
        """
        合成代码
        :param in_raster_files:
        :param out_raster_file:
        :param fill_value:
        :param model:
        :return:
        """

        if fill_value is None:  # 1. get fill_value
            ds = gdal.Open(in_raster_files[0])
            read_fill_value = ds.GetRasterBand(1).GetNoDataValue()
            if read_fill_value is None:
                fill_value = np.nan
            # else:
            # fill_value = np.finfo('f').min

        data, XSize, YSize, geotrans, proj = GeoProcessUtil.read_tiff(in_raster_files[0], 1)  # 2. get raster info
        if np.isnan(fill_value):
            idx = np.isnan(data)
        else:
            idx = data == fill_value

        mat = []
        for in_raster_file in in_raster_files:
            temp_data = GeoProcessUtil.read_tiff(in_raster_file, 1, buf_xsize=XSize, buf_ysize=YSize)[0]

            if np.isnan(fill_value):
                temp_idx = np.isnan(data)  # 4. 获取当前tif无效值的索引
                temp_data[np.isnan(temp_data)] = np.nan  # 4. 将无效值位置设为np.nan，不参与最大，最小，均值运算
            else:
                temp_idx = temp_data == fill_value
                temp_data[temp_data == fill_value] = np.nan

            idx = idx & temp_idx  # 5. 获取当前tif无效值  与  前面所有tif无效值  同一位置上都是无效值的索引   即：意在找出n个tif中都是无效值的位置
            mat.append(temp_data)

        stack_mat = np.dstack(mat)  # 6. 合成处理
        out_data = None  # 输出数据
        if model == "MEAN":
            # out_data = stack_mat.mean(axis=2)   # np.dstack的操作:stack_mat.mean(axis=2) ,但是不能过滤np.nan
            out_data = np.nanmean(stack_mat, axis=2)
        elif model == "MAX":
            out_data = np.nanmax(stack_mat, axis=2)
        elif model == "MIN":
            out_data = np.nanmin(stack_mat, axis=2)

        if np.isnan(fill_value) or (fill_value == np.finfo('f').min):  # 7. 无效值位置处理
            fill_value = -9999
        out_data[idx] = fill_value

        GeoProcessUtil.write_tiff(out_data, XSize, YSize, 1, geotrans, proj, out_raster_file, no_data_value=fill_value)
