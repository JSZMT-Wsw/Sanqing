# encoding: utf-8
"""
@author: DYX
@file: GeoProcessTools.py
@time: 2020/4/13 20:22
@desc:
"""
"""
RasterProcess:
    矢量裁剪栅格：
        1.clip_by_shp
        2.clip_by_shp_attribute
        3.clip_by_shp_attribute_while
    栅格数据镶嵌：
        1.raster_mosaic:  FIRST, LAST， MEAN， MINIMUM， MAXIMUM， SUM
    点(CIMISS)数据插值成tif   (.csv   .shp)
        1.interpolation_by_points  invdist: 反距离权重  invdistnn：XXX   average：移动平均法   nearest：最近邻法    linear：线性差值法
    hdf数据转tif
        1.hdf_correction_by_geoloc
        2.hdf_correction_by_gcp
        3.hdf_corretion_by_vrt
    几何校正:
        1.raster_corretion_by_rpc   自带rpc/rpb文件的地理数据处理
    栅格数据坐标系转换：
        1.raster_coordinaterans_by_tool
        2.raster_coordinaterans_by_vrt
    多期合成:
        1.raster_compose    MEAN    MIN     MAX
    栅格转矢量:
    快试图：
        1.quickview_by_raster
        2.dataview_by_raster    (效果不好，但提供一种方法)
        3.bandview_by_raster    (单波段赋色渲染  颜色参考链接:https://matplotlib.org/gallery/color/colormap_reference.html
                                https://matplotlib.org/gallery/color/named_colors.html#sphx-glr-gallery-color-named-colors-py)
    重采样：  scale   XSize和YSize的倍数
        1.raster_resize     NearestNeighbour    Bilinear    Cubic   CubicSpline
    创建金字塔：
        1.create_pyramid
    栅格数据格式转换：   HFA=img, GTiff=tif
        1.raster_format_trans_by_api
        2.raster_format_trans_by_copy
    
VectorProcess：
    矢量数据坐标系转换：
        1.vector_coordinaterans_by_tool
        2.vector_coordinaterans_by_api
    矢量要素分割
        1.split_by_attribute    单个要素
        2.split_by_attribute_while  遍历属性表
    面矢量转线矢量
        1.polygon_to_line
    合并矢量：
        1.aggregate_polygons
    矢量数据格式转换: "ESRI Shapefile"  "KML"  
        1.vector_format_trans_by_exe
    面矢量聚合：
        1.vector_polymerize
    点是否在矢量内:
        1.point_in_polygon
    矢量转栅格
        1.shp_to_raster
        
    
GdalBase:
    1.read_tiff
    2.write_tiff
    3.read_grib / grib数据解析

OgrBase
    矢量复制操作:
        1.copy_shp_by_datasource
        2.copy_shp_by_layer
        3.copy_shp_by_feature
    点生成点矢量
        1.create_point_shp
    新增属性表中的字段        
        1.add_fieldDefn  其中，类型必须用官方给定常量 ogr.OFTInteger/ogr.OFTString/ogr.OFTReal/ogr.OFTDate
    改变属性表中的字段属性
        1.alter_fieldDefn   其中，字典名必须用 name/type/width/precision (大小写无关)
    改变属性表中的某条记录某个字段的值
        1.alter_feature_value
    删除特定要素(行)
        1.delet_feature_by_fieldDefn
"""

"""
ESPG编号使用：
    EPSG编号    European Petroleum Survey Group
    http://epsg.io/?q=
    地理坐标系(从Arcgis中查找的编码)：
        EPSG:4214   Beijing 1954
        EPSG:4610   Xian 1980
        EPSG:4490   CGCS2000
        *EPSG:4326   WGS 84  Geodetic coordinate system(地理坐标系)
    投影坐标系:
        *EPSG:3857   WGS 84 / Pseudo-Mercator -- Spherical Mercator, Google Maps, OpenStreetMap, Bing, ArcGIS, ESRI
        EPSG:3395   WGS 84 World Mercator
    CGCS2000
        EPSG:4479 China Geodetic Coordinate System 2000   以地球的几何球心为中心   (该编号输出错误)
        EPSG:4480 China Geodetic Coordinate System 2000   以地球的椭球焦点为中心   (该编号不能被代码识别)
        EPSG:4490
"""

import warnings

warnings.filterwarnings('ignore')
import time
import shutil
import os
import sys
import re
import cv2
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from skimage import exposure
# from scipy.misc import bytescale
import xml.dom.minidom
import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal, ogr, osr
from shapely.geometry import Point, MultiPolygon
from shapely.wkt import loads, dumps
from shapely.ops import cascaded_union

gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
gdal.SetConfigOption("SHAPE_ENCODING", "utf-8")
ogr.RegisterAll()


class RasterProcess:
	"""栅格数据处理"""
	
	@staticmethod
	def clip_by_shp(in_raster_file, shp_file, out_raster_file=None):
		"""
		矢量裁剪栅格(矢量外边界)
		:param in_raster_file: string  in put shp file
		:param shp_file:
		:param out_raster_file:
		:return:
		"""

		if isinstance(in_raster_file, gdal.Dataset):
			ds_raster = in_raster_file
		else:
			ds_raster = gdal.Open(in_raster_file)

		# ds_raster = gdal.Open(in_raster_file)
		
		ds_shp = ogr.Open(shp_file)
		layer = ds_shp.GetLayer()
		extent = layer.GetExtent()  # 西，东，南，北
		output_bounds_args = (extent[0], extent[2], extent[1], extent[3])
		
		if out_raster_file is None:
			file_ary = os.path.splitext(in_raster_file)
			out_raster_file = file_ary[0] + "_clip" + file_ary[1]
		
		gdal.Warp(out_raster_file, ds_raster, format="GTiff", cutlineDSName=shp_file, outputBounds=output_bounds_args,
		          # callback=gdal.TermProgress
		          )
		
		ds_shp.Destroy()
		del ds_raster
		return out_raster_file
	
	@staticmethod
	def clip_by_shp_attribute(in_raster_file, shp_file, **kwargs):
		"""
		矢量裁剪栅格(矢量属性)
		:param in_raster_file: str
		:param shp_file:s tr
		:param kwargs: attri=value  ID=3201, NAME=南京
		:return:
		"""
		out_raster_files = []
		
		ds_raster = gdal.Open(in_raster_file)
		
		ds_shp = ogr.Open(shp_file)
		layer = ds_shp.GetLayer()
		feature = layer.GetFeature(0)
		field_names = feature.keys()
		
		for key, value in kwargs.items():
			if key not in field_names:  # attri is in shp fieldDefn
				print("Field not in shp")
				break
			
			field_values = []
			layer.ResetReading()
			feature = layer.GetNextFeature()
			while feature:
				field_values.append(feature.GetField(key))
				feature = layer.GetNextFeature()
			field_values = [str(x) for x in field_values]
			
			if str(value) not in field_values:  # value is in shp attri
				print("attri has no input args value")
				return
			idx = field_values.index(str(value))  # get feature idx
			
			file_ary = os.path.splitext(in_raster_file)
			temp_raster_files = file_ary[0] + "_" + str(value) + "_clip" + file_ary[1]  # get outfile  path
			
			cutline_where_args = key + " = " + "\'" + str(value) + "\'"  # filter continue
			
			feature = layer.GetFeature(idx)
			geom = feature.GetGeometryRef()
			envelope = geom.GetEnvelope()
			output_bounds_args = (envelope[0], envelope[2], envelope[1], envelope[3])  # feature envelope
			
			gdal.Warp(temp_raster_files, ds_raster, format="GTiff", cutlineDSName=shp_file,
			          cutlineWhere=cutline_where_args, outputBounds=output_bounds_args)
			
			out_raster_files.append(temp_raster_files)
		
		ds_shp.Destroy()
		del ds_raster
		return out_raster_files
	
	@staticmethod
	def clip_by_shp_attribute_while(in_raster_file, shp_file, attribute):
		"""
		:param in_raster_file: str
		:param shp_file: str
		:param attribute: str
		:return:
		"""
		out_raster_files = []
		
		ds_raster = gdal.Open(in_raster_file)
		srcNodata = ds_raster.GetRasterBand(1).GetNoDataValue()
		if srcNodata is None:
			dstNodata = 0
		else:
			dstNodata = srcNodata
		
		ds_shp = ogr.Open(shp_file)
		layer = ds_shp.GetLayer()
		feature = layer.GetFeature(0)
		field_names = feature.keys()
		if str(attribute) not in field_names:
			print("input attribute not in shp attri")
			return
		
		layer.ResetReading()
		feature = layer.GetNextFeature()
		while feature:
			field_value = feature.GetField(str(attribute))  # get cur_feature value
			
			file_ary = os.path.splitext(in_raster_file)
			temp_raster_files = file_ary[0] + "_" + str(field_value) + "_clip" + file_ary[1]  # get outfile  path
			
			cutline_where_args = attribute + " = " + "\'" + str(field_value) + "\'"  # filter continue
			
			geom = feature.GetGeometryRef()
			envelope = geom.GetEnvelope()
			output_bounds_args = (envelope[0], envelope[2], envelope[1], envelope[3])  # feature envelope
			
			gdal.Warp(temp_raster_files, ds_raster, format="GTiff", cutlineDSName=shp_file,
			          srcNodata=dstNodata, dstNodata=dstNodata,
			          cutlineWhere=cutline_where_args, outputBounds=output_bounds_args, callback=gdal.TermProgress)
			out_raster_files.append(temp_raster_files)
			
			feature = layer.GetNextFeature()
		
		ds_shp.Destroy()
		del ds_raster
		return out_raster_files
	
	@staticmethod
	def raster_mosaic(out_raster_file, mosaic_type, srcNodata, dstNodata, args):
		"""
		栅格数据镶嵌
		:param out_raster_file:
		:param mosaic_type: str UPPER， FIRST, LAST， MEAN， MINIMUM， MAXIMUM， SUM   重叠区域处理方式
		:param srcNodata:
		:param dstNodata:
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
				ds = RasterProcess.mosaic_func(args[0], args[1], srcNodata, dstNodata, mosaic_type)
				for cur_raster_file in args[2:]:
					ds = RasterProcess.mosaic_func(ds, cur_raster_file, srcNodata, dstNodata, mosaic_type)
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
		
		data_befor, XSize, YSize, geotrans, proj = GdalBase.read_tiff(temp_ds_befor, 1)
		data_after = GdalBase.read_tiff(temp_ds_after, 1)[0]
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
		
		out_ds = GdalBase.write_tiff(out_data, XSize, YSize, 1, geotrans, proj, no_data_value=dstNodata,
		                             return_mode="MEMORY")
		
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
			vrt_file = RasterProcess.write_vrt(in_file, z_field, vrt_file)  # write vrt file
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
		out_raster_file = RasterProcess.clip_by_shp(interpolation_file, shp_file, out_raster_file)
		
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
			file_write.write('\t\t<GeometryField encoding="PointFromColumns" x="LONGITUDE" y="LATITUDE" z="%s"/>\n' % z_filed)
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
			print(sub[0])
			print(re.split(r'[:|//|\t|,]', sub[0].strip())[-1])  # 字符串以",", "//", "\t" ":" 分割
			if re.split('[:|//|\t|,]', sub[0])[-1] == dataset_name:
				break
			else:
				count += 1
		del ds, subdatasets
		
		if count != item: return
		
		return count
	
	@staticmethod
	def hdf_correction_by_geoloc(in_hdf_file, dataset_name, out_raster_file=None, fill_value_key=None):
		"""
		:param in_hdf_file:
		:param dataset_name:
		:param out_raster_file:
		:return:
		"""
		
		count = RasterProcess.get_dataset_idx(in_hdf_file, dataset_name)
		
		ds = gdal.Open(in_hdf_file)
		subdatasets = ds.GetSubDatasets()
		sub_ds = gdal.Open(subdatasets[count][0])  # 1. get sub dataset
		
		p = sub_ds.RasterCount
		data_type = sub_ds.GetRasterBand(1).DataType  # 2. get args
		if fill_value_key is None:
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
		                   srcNodata=fill_value, dstNodata=0,
		                   resampleAlg=gdal.GRIORA_Bilinear,
		                   outputType=data_type,
		                   callback=gdal.TermProgress)
		del ds, sub_ds
		
		if out_raster_file is None:
			return out_ds
		else:
			return out_raster_file
	
	@staticmethod
	def hdf_correction_by_gcp(in_hdf_file, dataset_name, fill_value, lon_key, lat_key,
	                          resolution_lon__key, resolution_lat__key,
	                          out_raster_file=None):
		"""

		:param in_hdf_file:
		:param dataset_name:
		:param fill_value:
		:param lon_key:
		:param lat_key:
		:param resolution_lon__key:
		:param resolution_lat__key:
		:param out_raster_file:
		:return:
		"""
		
		count = RasterProcess.get_dataset_idx(in_hdf_file, dataset_name)
		
		ds = gdal.Open(in_hdf_file)
		subdatasets = ds.GetSubDatasets()
		sub_ds = gdal.Open(subdatasets[count][0])
		
		XSize = sub_ds.RasterXSize
		YSize = sub_ds.RasterYSize
		dataType = sub_ds.GetRasterBand(1).DataType
		
		metadata = sub_ds.GetMetadata()
		lon = metadata[lon_key].split()
		lon = [float(x) for x in lon]
		lat = metadata[lat_key].split()
		lat = [float(x) for x in lat]
		
		xRes_args = float(metadata[resolution_lon__key].strip())
		yRes_args = float(metadata[resolution_lat__key].strip())
		
		# gdal.GCP([x], [y], [z], [pixel], [line], [info], [id])
		# x、y、z是控制点对应的投影坐标，默认为0;
		# pixel、line是控制点在图像上的列、行位置，默认为0;
		# info、id是用于说明控制点的描述和点号的可选字符串，默认为空
		gcps_list = [gdal.GCP(min(lon), max(lat), 0, 0, 0),
		             gdal.GCP(max(lon), max(lat), 0, XSize, 0),
		             gdal.GCP(min(lon), min(lat), 0, 0, YSize),
		             gdal.GCP(max(lon), min(lat), 0, XSize, YSize)]
		
		sr = osr.SpatialReference()
		sr.SetWellKnownGeogCS('WGS84')  # 添加空间参考
		sub_ds.SetGCPs(gcps_list, sr.ExportToWkt())  # 添加控制点
		
		if out_raster_file is None:
			out_raster_file_args = ""
			format_args = "MEM"
		else:
			out_raster_file_args = out_raster_file
			format_args = "GTiff"
		
		out_ds = gdal.Warp(out_raster_file_args, sub_ds, format=format_args, tps=True,
		                   xRes=xRes_args, yRes=yRes_args,
		                   dstNodata=fill_value, srcNodata=fill_value,
		                   resampleAlg=gdal.GRIORA_NearestNeighbour,
		                   outputType=dataType)
		
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
		count = RasterProcess.get_dataset_idx(in_hdf_file, dataset_name)
		
		ds = gdal.Open(in_hdf_file)
		subdatasets = ds.GetSubDatasets()
		sub_ds = gdal.Open(subdatasets[count][0])
		
		file_ary = os.path.splitext(in_hdf_file)
		vrt_file = file_ary[0] + ".vrt"
		gdal.Translate(vrt_file, sub_ds, format="VRT")
		
		sr = osr.SpatialReference()
		sr.ImportFromEPSG(4326)  # 添加空间参考
		
		lonDS = subdatasets[RasterProcess.get_dataset_idx(in_hdf_file, lon_key)][0]
		latDS = subdatasets[RasterProcess.get_dataset_idx(in_hdf_file, lat_key)][0]
		
		# data mate / lon mate   for example: modis data is 2030x1354, but lon and lat is 406x271, 5times
		line_step = int(sub_ds.RasterXSize / gdal.Open(lonDS).RasterXSize)
		pixel_step = int(sub_ds.RasterYSize / gdal.Open(latDS).RasterYSize)
		
		RasterProcess.update_vrt(vrt_file, sr.ExportToWkt(), lonDS, latDS, line_step, pixel_step)
		
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
	def raster_corretion_by_rpc(in_raster_file, out_raster_file):
		"""
		栅格数据 rpb校正
		:param in_raster_file:
		:param rpb_file:
		:param out_raster_file:
		:return:
		"""
		
		ds_raster = gdal.Open(in_raster_file)
		nodata = ds_raster.GetRasterBand(1).GetNoDataValue()
		if nodata is None:
			nodata = 0.0
		
		gdal.Warp(out_raster_file, ds_raster, format="GTiff", rpc=True, srcNodata=nodata, dstNodata=nodata,
		          callback=gdal.TermProgress)
		del ds_raster
	
	@staticmethod
	def raster_coordinaterans_by_tool(in_raster_file, out_raster_file, dst_srs):
		"""
		栅格数据坐标系转换
		:param in_raster_file:
		:param out_raster_file:
		:param dst_srs: dst_srs = osr.SpatialReference()    dst_srs.ImportFromEPSG(102025)
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
		print("源文件坐标系{0}".format(src_srs_WKID))
		
		dst_srs_WKID = dst_srs.GetAttrValue('AUTHORITY', 1)
		print("目标文件坐标系{0}".format(dst_srs_WKID))
		
		gdal.Warp(out_raster_file, ds, format="GTiff", dstSRS=dst_srs.ExportToWkt(), resampleAlg=gdal.GRIORA_Bilinear,
		          srcNodata=dstNodata, dstNodata=dstNodata, callback=gdal.TermProgress)
		
		del ds
		return out_raster_file
	
	@staticmethod
	def raster_coordinaterans_by_vrt(in_raster_file, out_raster_file, dst_srs):
		"""
		:param in_raster_file:
		:param out_raster_file:
		:param dst_srs:
		:return:
		"""
		ds = gdal.Open(in_raster_file)
		sp = ds.GetProjection()
		
		src_srs = osr.SpatialReference()
		src_srs.ImportFromWkt(sp)
		src_srs_WKID = src_srs.GetAttrValue('AUTHORITY', 1)
		print("源文件坐标系{0}".format(src_srs_WKID))
		
		dst_srs_WKID = dst_srs.GetAttrValue('AUTHORITY', 1)
		print("目标文件坐标系{0}".format(dst_srs_WKID))
		
		vrt_ds = gdal.AutoCreateWarpedVRT(ds, None, dst_srs.ExportToWkt(), gdal.GRA_Bilinear)
		gdal.GetDriverByName('GTiff').CreateCopy(out_raster_file, vrt_ds, 0, callback=gdal.TermProgress)
		
		del ds, vrt_ds
		
		return out_raster_file
	
	@staticmethod
	def raster_compose(in_raster_files, out_raster_file, fill_value=None, model="MEAN"):
		"""

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
			else:
				
				fill_value = np.finfo('f').min
		
		data, XSize, YSize, geotrans, proj = GdalBase.read_tiff(in_raster_files[0], 1)  # 2. get raster info
		if np.isnan(fill_value):
			idx = np.isnan(data)
		else:
			idx = data == fill_value
		
		mat = []
		for in_raster_file in in_raster_files:
			temp_data = GdalBase.read_tiff(in_raster_file, 1, buf_xsize=XSize, buf_ysize=YSize)[0]
			
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
		
		if np.isnan(fill_value) or (fill_value == np.finfo('f')).min:  # 7. 无效值位置处理
			fill_value = -9999
		out_data[idx] = fill_value
		
		GdalBase.write_tiff(out_data, XSize, YSize, 1, geotrans, proj, out_raster_file, no_data_value=fill_value)
	
	@staticmethod
	# TODO
	def raster_to_polygonize(in_raster_file, idxband, out_shp_file):
		
		sourceRaster = gdal.Open(in_raster_file)
		srcBand = sourceRaster.GetRasterBand(idxband)
		maskBand = srcBand.GetMaskBand()
		
		driver = ogr.GetDriverByName("ESRI Shapefile")
		if os.access(out_shp_file, os.F_OK):
			driver.DeleteDataSource(out_shp_file)
		dst_ds = driver.CreateDataSource(out_shp_file)
		
		srs = osr.SpatialReference()
		srs.ImportFromWkt(sourceRaster.GetProjectionRef())
		outLayer = dst_ds.CreateLayer(out_shp_file, srs)
		
		fieldDenf = ogr.FieldDefn('Class', ogr.OFTInteger)
		outLayer.CreateField(fieldDenf)
		
		gdal.Polygonize(srcBand, None, outLayer, 0, options=[], callback=gdal.TermProgress)
		
		dst_ds.Destroy()
		sourceRaster = None
	
	# @staticmethod
	# def quickview_by_raster(out_png_file, rgb_index, scale, gamma, *args):
		# """
		# 栅格数据出快试图
		# :param out_png_file: str 快视图路径
		# :param rgb_index: list rgb对应的波段索引
		# :param scale: float 伸缩因子 【0~1】
		# :param gamma: float 亮度因子  >1: 变暗； <1:变亮   =1：原亮度
		# :param args: 输入栅格数据
		# :return:
		# """
		# if len(args) == 0:
			# print("No raster input!")
			# return

		# scale = float(scale)
		# gamma = float(gamma)

		# r, g, b = None, None, None
		# if len(args) == 1:
			# in_raster_file = args[0]
			# r = GdalBase.read_tiff(in_raster_file, rgb_index[0], scale)[0]
			# g = GdalBase.read_tiff(in_raster_file, rgb_index[1], scale)[0]
			# b = GdalBase.read_tiff(in_raster_file, rgb_index[2], scale)[0]  # 1. get tif data
		# elif len(args) == 2:
			# max_idx = max(rgb_index)
			# if max_idx > 2:
				# print("input files is less")
				# return
			# in_raster_files = list(args)
			# in_raster_files.insert(0, "null")
			# r = GdalBase.read_tiff(in_raster_files[rgb_index[0]], 1, scale)[0]
			# g = GdalBase.read_tiff(in_raster_files[rgb_index[1]], 1, scale)[0]
			# b = GdalBase.read_tiff(in_raster_files[rgb_index[2]], 1, scale)[0]
		# elif len(args) >= 3:
			# in_raster_files = list(args)
			# in_raster_files.insert(0, "null")
			# r = GdalBase.read_tiff(in_raster_files[rgb_index[0]], 1, scale)[0]
			# g = GdalBase.read_tiff(in_raster_files[rgb_index[1]], 1, scale)[0]
			# b = GdalBase.read_tiff(in_raster_files[rgb_index[2]], 1, scale)[0]

		# ds = gdal.Open(args[0])
		# fill_value = ds.GetRasterBand(1).GetNoDataValue()
		# del ds

		# index = np.where((b == fill_value) & (g == fill_value) & (r == fill_value))
		# if len(index[0]) == 0:
			# index = np.where((b == 0.0) & (g == 0.0) & (r == 0.0))

		# r[index] = 0.
		# g[index] = 0.
		# b[index] = 0.  # 2. background value fill 0

		# r_scale = bytescale(r)
		# g_scale = bytescale(g)
		# b_scale = bytescale(b)  # 3. data trans 0~255

		# img_scale = cv2.merge((b_scale, g_scale, r_scale))

		# img_LAB = cv2.cvtColor(img_scale, cv2.COLOR_BGR2LAB)
		# (bL, gL, rL) = cv2.split(img_LAB)
		# clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(10, 10))
		# claheB = clahe.apply(np.array(bL, dtype=np.uint8))
		# img_clahe = cv2.merge((claheB, gL, rL))
		# imgColor = cv2.cvtColor(img_clahe, cv2.COLOR_LAB2BGR)  # 5. 自适应直方图均衡化

		# imgColor_gamma = exposure.adjust_gamma(imgColor, gamma)  # 6. 亮度调整

		# (bC, gC, rC) = cv2.split(imgColor_gamma)
		# bC[index] = 255
		# gC[index] = 255
		# rC[index] = 255

		# alpha_channel = np.ones(bC.shape, dtype=bC.dtype) * 255
		# alpha_channel[index] = 0
		# img = cv2.merge((bC, gC, rC, alpha_channel))  # 7. 设置透明

		# cv2.imwrite(out_png_file, img, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
	
	@staticmethod
	def dataview_by_raster(out_png_file, rgb_index, *args):
		"""
		:param out_png_file:
		:param rgb_index:
		:param args:
		:return:
		"""
		if len(args) == 0:
			print("No raster input!")
			return
		
		r, g, b = None, None, None
		if len(args) == 1:
			in_raster_file = args[0]
			RasterProcess.create_pyramid(in_raster_file)
			
			r = RasterProcess.get_overview_data(in_raster_file, band_index=rgb_index[0])
			g = RasterProcess.get_overview_data(in_raster_file, band_index=rgb_index[1])
			b = RasterProcess.get_overview_data(in_raster_file, band_index=rgb_index[2])
		
		elif len(args) == 2:
			max_idx = max(rgb_index)
			if max_idx > 2:
				print("input files is less")
				return
			in_raster_files = list(args)
			in_raster_files.insert(0, "null")
			
			RasterProcess.create_pyramid(in_raster_files[rgb_index[0]])
			r = RasterProcess.get_overview_data(in_raster_files[rgb_index[0]], band_index=1)
			
			RasterProcess.create_pyramid(in_raster_files[rgb_index[1]])
			g = RasterProcess.get_overview_data(in_raster_files[rgb_index[1]], band_index=1)
			
			RasterProcess.create_pyramid(in_raster_files[rgb_index[2]])
			b = RasterProcess.get_overview_data(in_raster_files[rgb_index[2]], band_index=1)
		
		elif len(args) >= 3:
			in_raster_files = list(args)
			in_raster_files.insert(0, "null")
			
			RasterProcess.create_pyramid(in_raster_files[rgb_index[0]])
			r = RasterProcess.get_overview_data(in_raster_files[rgb_index[0]], band_index=1)
			
			RasterProcess.create_pyramid(in_raster_files[rgb_index[1]])
			g = RasterProcess.get_overview_data(in_raster_files[rgb_index[1]], band_index=1)
			
			RasterProcess.create_pyramid(in_raster_files[rgb_index[2]])
			b = RasterProcess.get_overview_data(in_raster_files[rgb_index[2]], band_index=1)
		
		r = RasterProcess.stretch_data(r, 2)
		g = RasterProcess.stretch_data(g, 2)
		b = RasterProcess.stretch_data(b, 2)
		alpha = np.where(r + g + b > 0, 1, 0)
		
		data = np.dstack((r, g, b, alpha))
		plt.imshow(data)
		plt.xticks([])  # 轴不可见
		plt.yticks([])
		plt.axis('off')  # 去除边框
		plt.savefig(out_png_file, transparent=True)
	
	@staticmethod
	def bandview_by_raster(in_raster_file, color, out_png_file):
		"""
		:param in_raster_file:
		:param color:
		:param out_png_file:
		:return:
		"""
		# RasterProcess.create_pyramid(in_raster_file)
		# data = RasterProcess.get_overview_data(in_raster_file)
		
		data = GdalBase.read_tiff(in_raster_file, 1)[0]
		
		mean = np.nanmean(data)
		std_range = np.nanstd(data) * 2
		data = np.ma.masked_equal(data, 0)
		plt.imshow(data, cmap=color, vmin=mean - std_range, vmax=mean + std_range)
		
		plt.xticks([])  # 轴不可见
		plt.yticks([])
		plt.axis('off')  # 去除边框
		plt.savefig(out_png_file, transparent=True)
	
	@staticmethod
	def get_overview_data(fn, band_index=1, level=1):
		"""
		:param fn:
		:param band_index:
		:param level:
		:return:
		"""
		
		# band_index = int(band_index)
		# level = float(level)
		
		ds = gdal.Open(fn)
		band = ds.GetRasterBand(band_index)
		if level > 0:
			ov_band = band.GetOverview(level)
		else:
			num_ov = band.GetOverviewCount()
			ov_band = band.GetOverview(num_ov + level)
		return ov_band.ReadAsArray()
	
	@staticmethod
	def stretch_data(data, num_stddev):
		"""
		:param data:
		:param num_stddev:
		:return:
		"""
		mean = np.mean(data)
		std_range = np.std(data) * num_stddev
		
		new_min = max(mean - std_range, np.min(data))
		new_max = min(mean + std_range, np.max(data))
		clipped_data = np.clip(data, new_min, new_max)
		return clipped_data / (new_max - new_min)
	
	@staticmethod
	def raster_resize(in_raster_file, scale, model="NearestNeighbour", out_raster_file=None):
		"""
		:param in_raster_file:
		:param scale:
		:param model:
		:param out_raster_file:
		:return:
		"""
		src_ds = gdal.Open(in_raster_file)
		geoTrans = src_ds.GetGeoTransform()
		
		scale = float(scale)
		xRes = geoTrans[1] * scale
		yRes = geoTrans[1] * scale
		
		if model == "NearestNeighbour":
			model = gdal.GRA_NearestNeighbour
		elif model == "Bilinear":
			model = gdal.GRA_Bilinear
		elif model == "Cubic":
			model = gdal.GRA_Cubic
		elif model == "CubicSpline":
			model = gdal.GRA_CubicSpline
		
		if out_raster_file is None:
			out_ds = gdal.Warp("", src_ds, xRes=xRes, yRes=yRes, resampleAlg=model, callback=gdal.TermProgress)
			return out_ds
		else:
			gdal.Warp(out_raster_file, src_ds, xRes=xRes, yRes=yRes, resampleAlg=model, callback=gdal.TermProgress)
			return out_raster_file
	
	@staticmethod
	def create_pyramid(in_raster_file):
		"""
		:param in_raster_file:
		:return:
		"""
		ds = gdal.Open(in_raster_file)
		ds.BuildOverviews(overviewlist=[2, 4, 8, 16, 32, 64, 128], callback=gdal.TermProgress)
	
	@staticmethod
	def raster_format_trans_by_api(in_raster_file, out_raster_file, format):
		"""
		栅格数据格式转换    gdal.Translate API接口
		:param in_raster_file:
		:param out_raster_file:
		:param format
		:return:
		"""
		drv_count = gdal.GetDriverCount()
		sup_drv = [gdal.GetDriver(idx).ShortName for idx in range(drv_count)]
		if format not in sup_drv:
			print("out raster driver is not support")
			return
		
		ds = gdal.Open(in_raster_file)
		gdal.Translate(out_raster_file, ds, format=format, callback=gdal.TermProgress)
		ds = None
	
	@staticmethod
	def raster_format_trans_by_copy(in_raster_file, out_raster_file, format):
		"""
		栅格数据格式转换    driver.CreateCopy(dst_filename, src_ds, 0)
		:param in_raster_file:
		:param out_raster_file:
		:param format
		:return:
		"""
		drv_count = gdal.GetDriverCount()
		sup_drv = [gdal.GetDriver(idx).ShortName for idx in range(drv_count)]
		if format not in sup_drv:
			print("out raster driver is not support")
			return
		
		src_ds = gdal.Open(in_raster_file)
		
		driver = gdal.GetDriverByName(format)
		dst_ds = driver.CreateCopy(out_raster_file, src_ds, 0, [], callback=gdal.TermProgress)
		
		dst_ds = None
		src_ds = None


class VectorProcess:
	@staticmethod
	def vector_coordinaterans_by_tool(in_shp_file, out_shp_file, dst_srs):
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
		print("源文件坐标系{0}".format(src_srs_WKID))
		
		dst_srs_WKID = dst_srs.GetAttrValue('AUTHORITY', 1)
		print("目标文件坐标系{0}".format(dst_srs_WKID))
		
		gdal.VectorTranslate(out_shp_file, in_shp_file, dstSRS=dst_srs.ExportToWkt(), reproject=True)
		ds.Destroy()
		return out_shp_file
	
	@staticmethod
	def vector_coordinaterans_by_api(in_shp_file, out_shp_file, dst_srs):
		"""
		:param in_shp_file:
		:param out_shp_file:
		:param dst_srs:
		:return:
		"""
		driver = ogr.GetDriverByName("ESRI Shapefile")
		if os.access(out_shp_file, os.F_OK):
			driver.DeleteDataSource(out_shp_file)
		
		src_ds = ogr.Open(in_shp_file, 0)
		src_layer = src_ds.GetLayer()
		spatialRef = src_layer.GetSpatialRef()
		wkt = spatialRef.ExportToWkt()
		
		src_feature = src_layer.GetFeature(0)
		src_geom = src_feature.GetGeometryRef()
		geom_type = src_geom.GetGeometryName()
		
		src_srs = osr.SpatialReference()
		src_srs.ImportFromWkt(wkt)
		src_srs_WKID = src_srs.GetAttrValue('AUTHORITY', 1)  # EPSG格式
		print("源文件坐标系{0}".format(src_srs_WKID))
		
		dst_srs_WKID = dst_srs.GetAttrValue('AUTHORITY', 1)
		print("目标文件坐标系{0}".format(dst_srs_WKID))
		
		coordTrans = osr.CoordinateTransformation(src_srs, dst_srs)
		
		dst_ds = driver.CreateDataSource(out_shp_file)
		dst_geom_type = None
		if geom_type == "POLYGON":
			dst_geom_type = ogr.wkbPolygon
		elif geom_type == "POINT":
			dst_geom_type = ogr.wkbPoint
		elif geom_type == "LINESTRING":
			dst_geom_type = ogr.wkbLineString
		dst_layer = dst_ds.CreateLayer("layer_oyt", dst_srs, geom_type=dst_geom_type)
		
		src_featureDefn = src_layer.GetLayerDefn()
		for i in range(src_featureDefn.GetFieldCount()):
			field_defn = src_featureDefn.GetFieldDefn(i)
			dst_layer.CreateField(field_defn)
		
		src_layer.ResetReading()
		src_feature = src_layer.GetNextFeature()
		while src_feature:
			geom = src_feature.GetGeometryRef()
			geom.Transform(coordTrans)
			
			dst_feature = ogr.Feature(src_featureDefn)
			dst_feature.SetGeometry(geom)
			
			for i in range(src_featureDefn.GetFieldCount()):
				field_defn = src_featureDefn.GetFieldDefn(i)
				field_name = field_defn.GetName()
				
				if field_defn.GetType() == 4:  #
					field_value = src_feature.GetField(field_name).decode('utf8').encode('gb2312')  # 转中文
				else:
					field_value = src_feature.GetField(field_name)
				dst_feature.SetField(field_name, field_value)
			
			dst_layer.CreateFeature(dst_feature)
			src_feature = src_layer.GetNextFeature()
		dst_ds.Destroy()
		src_ds.Destroy()
	
	@staticmethod
	def split_by_attribute(in_shp_file, **kwargs):
		"""

		:param in_shp_file:
		:param kwargs:
		:return:
		"""
		
		out_shp_files = []
		
		ds = ogr.Open(in_shp_file)
		layer = ds.GetLayer()
		feature = layer.GetFeature(0)
		field_names = feature.keys()
		
		for key, value in kwargs.items():
			if key not in field_names:
				print("Field not in shp")
				break
			
			field_values = []
			layer.ResetReading()
			feature = layer.GetNextFeature()
			while feature:
				field_values.append(feature.GetField(key))
				feature = layer.GetNextFeature()
			field_values = [str(x) for x in field_values]
			
			if str(value) not in field_values:
				print("attri has no input args value")
				return
			
			file_ary = os.path.splitext(in_shp_file)
			temp_raster_files = file_ary[0] + "_" + key + "_split" + file_ary[1]
			
			attribute_filter = key + " = " + "\'" + str(value) + "\'"
			layer.SetAttributeFilter(attribute_filter)
			
			OgrBase.copy_shp_by_layer(layer, temp_raster_files)
			out_shp_files.append(temp_raster_files)
		
		ds.Destroy()
		return out_shp_files
	
	@staticmethod
	def split_by_attribute_while(in_shp_file, attribute):
		"""
		:param in_shp_file:
		:param attribute:
		:return:
		"""
		
		out_shp_files = []
		
		ds_shp = ogr.Open(in_shp_file)
		layer = ds_shp.GetLayer()
		feature = layer.GetFeature(0)
		field_names = feature.keys()
		
		if str(attribute) not in field_names:
			print("input attribute not in shp attri")
			return
		
		field_values = []
		layer.ResetReading()
		feature = layer.GetNextFeature()
		while feature:
			field_values.append(feature.GetField(str(attribute)))
			feature = layer.GetNextFeature()
		field_values = [str(x) for x in field_values]
		ds_shp.Destroy()
		
		for field in field_values:
			attribute_filter = attribute + " = " + "\'" + str(field) + "\'"
			
			file_ary = os.path.splitext(in_shp_file)
			temp_raster_files = file_ary[0] + "_" + str(field) + "_split" + file_ary[1]
			
			ds_shp = ogr.Open(in_shp_file)
			layer = ds_shp.GetLayer()
			layer.SetAttributeFilter(attribute_filter)
			
			OgrBase.copy_shp_by_layer(layer, temp_raster_files)
			ds_shp.Destroy()
			
			out_shp_files.append(temp_raster_files)
		
		return out_shp_files
	
	@staticmethod
	def polygon_to_line(in_shp_file, out_shp_file):
		"""
		:param in_shp_file:
		:param out_shp_file:
		:return:
		"""
		driver = ogr.GetDriverByName('ESRI Shapefile')
		if os.access(out_shp_file, os.F_OK):
			driver.DeleteDataSource(out_shp_file)
		
		poly_ds = ogr.Open(in_shp_file)
		poly_sr = poly_ds.GetLayer().GetSpatialRef()
		
		line_ds = driver.CreateDataSource(out_shp_file)
		line_layer = line_ds.CreateLayer("layer", poly_sr, geom_type=ogr.wkbLineString)
		line_featureDefn = line_layer.GetLayerDefn()
		
		poly_layer = poly_ds.GetLayer()
		poly_layer.ResetReading()
		poly_feature = poly_layer.GetNextFeature()
		while poly_feature:
			geom = poly_feature.GetGeometryRef()
			geom_num = geom.GetGeometryCount()
			for idx in range(geom_num):
				ring = geom.GetGeometryRef(idx)
				
				out_feature = ogr.Feature(line_featureDefn)
				out_feature.SetGeometry(ring)
				line_layer.CreateFeature(out_feature)
				out_feature = None
			
			poly_feature = poly_layer.GetNextFeature()
		
		poly_ds.Destroy()
		line_ds.Destroy()
	
	@staticmethod
	def aggregate_polygons(in_shp_file, out_shp_file):
		"""

		:param in_shp_file:
		:return:
		"""
		ds = ogr.Open(in_shp_file, 1)
		in_layer = ds.GetLayer()
		
		driver = ogr.GetDriverByName("ESRI Shapefile")
		if os.access(out_shp_file, os.F_OK):
			driver.DeleteDataSource(out_shp_file)
		out_ds = driver.CreateDataSource(out_shp_file)
		out_layer = out_ds.CreateLayer("layer", in_layer.GetSpatialRef(), ogr.wkbPolygon)
		out_row = ogr.Feature(out_layer.GetLayerDefn())
		
		multipoly = ogr.Geometry(ogr.wkbMultiPolygon)
		
		for in_row in in_layer:
			in_geom = in_row.geometry().Clone()
			in_geom_type = in_geom.GetGeometryType()
			if in_geom_type == ogr.wkbPolygon:
				multipoly.AddGeometry(in_geom)
			elif in_geom_type == ogr.wkbMultiPolygon:
				for i in range(in_geom.GetGeometryCount()):
					multipoly.AddGeometry(in_geom.GetGeometryRef(i))
		
		multipoly = multipoly.UnionCascaded()
		out_row.SetGeometry(multipoly)
		out_layer.CreateFeature(out_row)
		
		ds.Destroy()
		out_ds.Destroy()
	
	@staticmethod
	def vector_format_trans_by_exe(in_shp_file, out_shp_file, format):
		"""
		矢量数据格式转换    调用ogr2ogr.exe
		:param in_shp_file:
		:param out_shp_file:
		:param format: ESRI Shapefile, KML
		:return:
		"""
		drv_count = ogr.GetDriverCount()
		sup_drv = [ogr.GetDriver(idx).name for idx in range(drv_count)]
		if format not in sup_drv:
			print("out vector driver is not support")
			return
		
		python_Interpreter_path = sys.executable.replace("\\", "/")  # 01获取python解释器路径
		ogr2ogr_exe_path = os.path.dirname(python_Interpreter_path) + "/Library/bin/ogr2ogr.exe"
		
		in_ext = os.path.splitext(in_shp_file)[1].upper()
		out_ext = os.path.splitext(out_shp_file)[1].upper()  # 02 获取输入输出文件后缀
		
		cmd_str = None
		if out_ext == ".KML" and format == "KML":  # shp -> kml
			cmd_str = ogr2ogr_exe_path + " -f " + format + " " + out_shp_file + " " + in_shp_file
		elif out_ext == ".SHP" and format == "ESRI Shapefile":  # kml -> shp
			cmd_str = ogr2ogr_exe_path + " " + out_shp_file + " " + in_shp_file
		elif in_ext == ".SHP" and out_ext == ".KMZ" and format == "KML":  # shp - >kmz
			cmd_str = ogr2ogr_exe_path + " -f " + format + " " + out_shp_file + " " + in_shp_file
		elif in_ext == ".KMZ" and out_ext == ".SHP" and format == "ESRI Shapefile":  # kmz - > shp
			cmd_str = ogr2ogr_exe_path + " " + out_shp_file + " " + in_shp_file
		elif (in_ext == ".KML" and out_ext == ".KMZ") or (in_ext == ".KMZ" and out_ext == ".KML"):
			shutil.copyfile(in_shp_file, out_shp_file)
			cmd_str = " "
		
		if cmd_str is not None:
			os.system(cmd_str)
		else:
			print("vector data format trans faild")
			return
	
	@staticmethod
	def vector_polymerize(in_shp_file, out_shp_file, pzfactor, fsfactor):
		"""
		矢量数据聚合
		:param in_shp_file: 输入shp 路径
		:param out_shp_file: 输出shp路径
		:param pzfacor: 膨胀因子
		:param fsfactor: 腐蚀因子
		:return:
		"""
		try:
			ds = ogr.Open(in_shp_file)
			layer = ds.GetLayer()
			
			layer.ResetReading()
			feature = layer.GetNextFeature()
			polygons = []
			while feature:
				geom = feature.GetGeometryRef()
				wkt = geom.ExportToWkt()
				
				poly = loads(wkt)
				dilated = poly.buffer(float(pzfactor))
				eroded = dilated.buffer(0)
				
				polygons.append(eroded)
				feature = layer.GetNextFeature()
			
			multipoly = cascaded_union(polygons)
			m = MultiPolygon(multipoly)
			m.buffer(float(fsfactor))
			multipoly_wkt = dumps(m)
			
			sr = osr.SpatialReference()
			sr.ImportFromEPSG(4326)
			
			driver = ogr.GetDriverByName("ESRI Shapefile")
			if os.access(out_shp_file, os.F_OK):
				driver.DeleteDataSource(out_shp_file)
			
			ds = driver.CreateDataSource(out_shp_file)
			layer = ds.CreateLayer("test", sr, ogr.wkbMultiPolygon)
			
			fieldDefn = ogr.FieldDefn("id", ogr.OFTString)
			layer.CreateField(fieldDefn)
			
			featureDefn = layer.GetLayerDefn()
			feature = ogr.Feature(featureDefn)
			
			geom = ogr.CreateGeometryFromWkt(multipoly_wkt)
			feature.SetGeometry(geom)
			feature.SetField("id", 1)
			layer.CreateFeature(feature)
			
			ds.Destroy()
			
			return True
		except:
			return False
	
	@staticmethod
	def point_in_polygon(lon, lat, in_shp_file):
		"""
		判断点是否在矢量内
		:param lon:
		:param lat:
		:param in_shp_file:
		:return:
		"""
		point = Point(float(lon), float(lat))  # 01 point shapely
		
		ds = ogr.Open(in_shp_file)
		layer = ds.GetLayer()
		feature_count = layer.GetFeatureCount()
		if feature_count > 1:  # 02 必须只有一个feature
			del ds
			file_ary = os.path.splitext(in_shp_file)
			out_shp_file = file_ary[0] + "_aggregate" + file_ary[1]
			VectorProcess.aggregate_polygons(in_shp_file, out_shp_file)
			ds = ogr.Open(out_shp_file)
			layer = ds.GetLayer()
		
		feature = layer.GetFeature(0)
		geom = feature.GetGeometryRef()
		wkt = geom.ExportToWkt()
		ply = loads(wkt)  # 03 获取多边形的shapely对象
		
		flag = point.within(ply)
		return flag
	
	@staticmethod
	def shp_to_raster(in_shp_file, cellsize, out_raster_file):
		
		cellsize = float(cellsize)
		
		ds_shp = ogr.Open(in_shp_file)
		in_layer = ds_shp.GetLayer()
		extent = in_layer.GetExtent()  # 西,东,南,北
		sp = in_layer.GetSpatialRef()
		wkt = sp.ExportToWkt()  # sp
		
		Xsize = int((extent[1] - extent[0]) / cellsize)
		Ysize = int((extent[3] - extent[2]) / cellsize)
		geo_transform = [extent[0], cellsize, 0.0, extent[3], 0.0, - cellsize]
		
		out_driver = gdal.GetDriverByName('GTiff')
		out_ds = out_driver.Create(out_raster_file, Xsize, Ysize, 1, gdal.GDT_Float32)
		out_ds.SetGeoTransform(geo_transform)
		out_ds.SetProjection(wkt)
		
		band = out_ds.GetRasterBand(1)
		band.SetNoDataValue(0)
		band.FlushCache()
		# gdal.RasterizeLayer(out_ds, [1], in_layer, options=['ID=val'])
		gdal.RasterizeLayer(out_ds, [1], in_layer, options=['ATTRIBUTE=shape_Area'], callback=gdal.TermProgress)
		# del out_ds
		ds_shp.Release()
		return out_raster_file


class GdalBase:
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
				print('read tiff success')
				return data, XSize, YSize,  bands, geotrans, proj
			else:
				print('error in read tiff')
		else:
			print('error in read tiff')
	
	@staticmethod
	def write_tiff(data, XSize, YSize, bands, geotrans, proj, out_path,
	               no_data_value=None, return_mode='TIFF'):
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
		if return_mode.upper() == 'MEMORY':
			return dataset
		elif return_mode.upper == 'TIFF':
			del dataset
	
	@staticmethod
	def read_grib(path, gribtype, band, out_text_file):
		"""
		grib数据解析
		:param path:    输入grib路径
		:param gribtype: grib数据类型：grib1或grib2   只能填1、非1
		:param band: 读取其中的第几层
		:param out_text_file:
		:return:
		"""
		cur_path = os.path.abspath(os.path.dirname(__file__))
		
		if gribtype == "1" or gribtype == 1:
			folder = 'grib1'
			exe_name = 'wgrib.exe'
		else:
			folder = 'grib2'
			exe_name = 'wgrib2.exe'
		grib_exe_path = cur_path + "/wgrib/" + folder + "/" + exe_name
		
		cmdstr = grib_exe_path + ' ' + path + ' -V ' + '-d ' + str(band) + ' -h -text -o ' + out_text_file
		os.system(cmdstr)


class OgrBase:
	@staticmethod
	def copy_shp_by_datasource():
		pass
	
	@staticmethod
	def copy_shp_by_layer(in_layer, out_shp_file):
		"""

		:param in_layer:
		:param out_shp_file:
		:return:
		"""
		driver = ogr.GetDriverByName('ESRI Shapefile')
		
		if os.access(out_shp_file, os.F_OK):
			driver.DeleteDataSource(out_shp_file)
		
		ds = driver.CreateDataSource(out_shp_file)
		layer = ds.CopyLayer(in_layer, "")
		ds.Destroy()
	
	@staticmethod
	def copy_shp_by_feature():
		pass
	
	@staticmethod
	def create_point_shp(in_file, out_shp_file):
		"""

		:param in_file:
		:param out_shp_file:
		:return:
		"""
		with open(in_file, "r") as file_read:
			datas = file_read.readlines()
		fields = re.split('[, \t]', datas[0].strip())  # 1. get eles name
		fields = [x if len(x) < 11 else x[:10] for x in fields]
		
		point_info = []
		for data in datas[1:]:
			temp_data = re.split('[, \t]', data.strip())
			data_list = [float(x) if item != 0 else x for item, x in enumerate(temp_data)]
			point_info.append(dict(zip(fields, data_list)))  # 2. get datas: [{}, {}...{}]
		
		type = [ogr.OFTReal] * len(fields)
		type[0] = ogr.OFTString  # station must first column  # 3. get elements
		
		driver = ogr.GetDriverByName("ESRI Shapefile")
		if os.access(out_shp_file, os.F_OK):
			driver.DeleteDataSource(out_shp_file)  # out file is exit
		
		sr = osr.SpatialReference()
		sr.ImportFromEPSG(4326)  # set srs
		
		ds = driver.CreateDataSource(out_shp_file)
		layer = ds.CreateLayer("layer", sr, ogr.wkbPoint)  # 4. create layer
		
		for item, field in enumerate(fields):  # 5.1 layer create fields
			fieldDefn = ogr.FieldDefn(field, type[item])
			layer.CreateField(fieldDefn)
		
		for record in point_info:
			featureDefn = layer.GetLayerDefn()
			feature = ogr.Feature(featureDefn)  # 6.1 open feature
			
			point = ogr.Geometry(ogr.wkbPoint)
			point.SetPoint(0, record["Lon"], record["Lat"])
			feature.SetGeometry(point)  # 6.2 feature add geometry
			
			for field in fields:
				feature.SetField(field, record[field])  # 6.3 feature  add field value
			
			layer.CreateFeature(feature)  # 5.2 layer create feature
		
		ds.Destroy()
		return out_shp_file
	
	@staticmethod
	def add_fieldDefn(in_shp_file, field_name, field_type, field_width=10, field_precision=4):
		"""
		:param in_shp_file:
		:param field_name:
		:param field_type: ogr.OFTInteger ogr.OFTString ogr.OFTReal ogr.OFTDate
		:param field_width:
		:param field_precision:
		:return:
		"""
		ds = ogr.Open(in_shp_file, 1)
		layer = ds.GetLayer()
		
		fieldDenf = ogr.FieldDefn(field_name, field_type)
		fieldDenf.SetWidth(int(field_width))
		fieldDenf.SetPrecision(int(field_precision))
		
		layer.CreateField(fieldDenf)
		ds.Destroy()
	
	@staticmethod
	def alter_fieldDefn(in_shp_file, field, **kwargs):
		"""
		:param in_shp_file:
		:param field:
		:param kwargs:name  type    width   precision
		:return:
		"""
		ds = ogr.Open(in_shp_file, 1)
		layer = ds.GetLayer()
		feature = layer.GetFeature(0)
		
		if field not in feature.keys():
			print("input field name not in table")
		
		feature_defn = layer.GetLayerDefn()
		idx = feature_defn.GetFieldIndex(field)
		
		alter_map = {}
		for key, value in kwargs.items():
			key = key.upper()
			alter_map[key] = value
		
		flag = None
		if "NAME" in alter_map.keys():
			new_name = alter_map["NAME"]
			flag = ogr.ALTER_NAME_FLAG
		else:
			new_name = feature_defn.GetFieldDefn(idx).GetName()
		
		if "TYPE" in alter_map.keys():
			new_type = alter_map["TYPE"]
			func = lambda x, y: x + y if x is not None else y
			flag = func(flag, ogr.ALTER_TYPE_FLAG)
		else:
			new_type = feature_defn.GetFieldDefn(idx).GetType()
		
		if "WIDTH" in alter_map.keys():
			new_width = alter_map["WIDTH"]
		else:
			new_width = feature_defn.GetFieldDefn(idx).GetWidth()
		
		if "PRECISION" in alter_map.keys():
			new_precision = alter_map["PRECISION"]
		else:
			new_precision = feature_defn.GetFieldDefn(idx).GetPrecision()
		
		if "WIDTH" in alter_map.keys() or "PRECISION" in alter_map.keys():
			func = lambda x, y: x + y if x is not None else y
			flag = func(flag, ogr.ALTER_WIDTH_PRECISION_FLAG)
		
		fld_defn = ogr.FieldDefn(new_name, new_type)
		fld_defn.SetWidth(int(new_width))
		fld_defn.SetPrecision(int(new_precision))
		layer.AlterFieldDefn(idx, fld_defn, flag)
		
		ds.Destroy()
	
	@staticmethod
	def alter_feature_value(in_shp_file, field_name, feat_value, **kwargs):
		"""
		修改值
		:param in_shp_file:
		:param field_name:
		:param fea_value:
		:param kwargs:
		:return:
		"""
		ds = ogr.Open(in_shp_file, 1)
		layer = ds.GetLayer()
		feature = layer.GetFeature(0)
		field_names = feature.keys()
		
		if field_name not in field_names:
			print("field name not in table")
			return
		
		for key, value in kwargs.items():
			if key not in field_names:
				print("field name not in table")
				return
			
			layer.ResetReading()
			feature = layer.GetNextFeature()
			while feature:
				if str(feature.GetField(field_name)) == feat_value:
					feature.SetField(key, value)
					layer.SetFeature(feature)
					break
				else:
					if layer.GetFeaturesRead() < layer.GetFeatureCount():
						feature = layer.GetNextFeature()
					else:
						print("feat value not in table")
						return
		ds.Destroy()
	
	@staticmethod
	def delet_feature_by_fieldDefn(in_shp_file, **kwargs):
		"""
		删除特定feature
		:param in_shp_file:
		:param kwargs:
		:return:
		"""
		ds = ogr.Open(in_shp_file, 1)
		layer = ds.GetLayer()
		feature = layer.GetFeature(0)
		fields_name = feature.keys()
		
		for key, value in kwargs.items():
			if key not in fields_name:
				print("field name not in table")
				return
			
			layer.ResetReading()
			for feature in layer:
				if feature.GetField(key) == value:
					layer.DeleteFeature(feature.GetFID())
					continue
		
		ds.ExecuteSQL('REPACK ' + layer.GetName())
		ds.ExecuteSQL('RECOMPUTE EXTENT ON ' + layer.GetName())
		ds.Destroy()


class OsrBase:
	def __init__(self):
		pass


class DataBase:
	@staticmethod
	def order_day(issue):
		"""
		:param issue:
		:return:
		"""
		issue = str(issue)
		if len(issue) < 8:
			print("input issue is error")
			return
		year = int(issue[0:4])
		month = int(issue[4:6])
		day = int(issue[6:8])
		
		dt = datetime(year, month, day)
		the_order_day = dt.strftime("%j")
		return int(the_order_day)
	
	@staticmethod
	def issue_day(year, delt_day):
		"""
		:param year:
		:param delt_day:
		:return:
		"""
		
		year = int(year)
		sta_dt = datetime(year, 1, 1)
		
		delt_day = int(delt_day)
		delt = timedelta(days=delt_day - 1)
		
		end_dt = (sta_dt + delt)
		the_issue_day = end_dt.strftime("%Y%m%d")
		return the_issue_day
	
	@staticmethod
	def getTimeRange(StartTime, EndTime, dataType):
		"""
		获取时间列表
		:param StartTime:
		:param EndTime:
		:param dataType: 间隔类型
		:return:
		"""
		StartTime = str(StartTime)
		EndTime = str(EndTime)
		
		timeRange = []
		if dataType == "MON":
			StartTime = str(StartTime[0:6] + "01000000")
			EndTime = str(EndTime[0:6] + "01000000")
			timeRange.append(StartTime)
			
			STimetoDate = datetime.strptime(StartTime, "%Y%m%d%H%M%S")  # str->date
			EdTimetoDate = datetime.strptime(EndTime, "%Y%m%d%H%M%S")
			
			while STimetoDate < EdTimetoDate:
				STimetoDate = STimetoDate + relativedelta(months=1)
				STimetoStr = STimetoDate.strftime("%Y%m%d%H%M%S")
				timeRange.append(STimetoStr)
		
		elif dataType == "DAY":
			StartTime = StartTime[0:8] + "000000"
			EndTime = EndTime[0:8] + "000000"
			timeRange.append(StartTime)
			
			STimetoDate = datetime.strptime(StartTime, "%Y%m%d%H%M%S")  # str->date
			EdTimetoDate = datetime.strptime(EndTime, "%Y%m%d%H%M%S")
			
			while STimetoDate < EdTimetoDate:
				STimetoDate = STimetoDate + relativedelta(days=1)
				STimetoStr = STimetoDate.strftime("%Y%m%d%H%M%S")
				timeRange.append(STimetoStr)
		
		elif dataType == "HOR":
			StartTime = StartTime[0:10] + "0000"
			EndTime = EndTime[0:10] + "0000"
			timeRange.append(StartTime)
			
			STimetoDate = datetime.strptime(StartTime, "%Y%m%d%H%M%S")  # str->date
			EdTimetoDate = datetime.strptime(EndTime, "%Y%m%d%H%M%S")
			
			while STimetoDate < EdTimetoDate:
				STimetoDate = STimetoDate + relativedelta(hours=1)
				STimetoStr = STimetoDate.strftime("%Y%m%d%H%M%S")
				timeRange.append(STimetoStr)
		
		return timeRange


# if __name__ == "__main__":
# 	t1 = time.time()
#
# 	hdf2 = r"F:\data\MCD19A2\MCD19A2.A2019244.h27v05.006.2019247202437.hdf"
# 	# hdf2 = r"C:\Users\dyx_giser\Desktop\MCD19A2.A2019244.h26v05.006.2019247203308.hdf"
# 	out_raster_file = r"F:\data\MCD19A2.A2019244.h27v05.006.2019247202437.tif"
#
# 	dataset_name = "Optical_Depth_055"
# 	fill_value_key = -28672
#
# 	RasterProcess.hdf_correction_by_geoloc(hdf2, dataset_name, out_raster_file=out_raster_file,
# 	                                             fill_value_key=fill_value_key)
#
# 	t2 = time.time()
# 	print(t2 - t1)
