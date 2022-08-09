# -*- coding:utf-8 -*-

import os

import arcpy

from src.common.utils.FileUtil import BaseFile
from src.common.utils.StringFormat import StringFormat


class ArcPyUtil:
	"""GIS工具类 TODO 待整理"""
	
	@staticmethod
	def creatJPG(lyr_path_dict, ele_dict, mxdDir, outDir, rasterPath, pluginName, areaInfo, issue, areaIDList):
		'''
		按照行政区划生成专题图 替换图层字典|替换文字字典|模板目录|输出目录|栅格tif文件路径|产品标识|当前行政区划|产品编号|行政区划ID列表
		返回信息[AreaID] = 专题图路径
		'''
		returnPathMap = {}
		try:
			BaseFile.creatDir(outDir)
			if BaseFile.isFileOrDir(mxdDir) != BaseFile.ISDIR or BaseFile.isFileOrDir(outDir) != BaseFile.ISDIR:
				return None
			if BaseFile.isFileOrDir(rasterPath) != BaseFile.ISFILE:
				return None
			if StringFormat.isEmpty(pluginName):
				return None
			if areaIDList is None or len(areaIDList) == 0:
				return None
			if lyr_path_dict is None or len(lyr_path_dict) == 0:
				return None
			
			mxdList = {}
			areaInfoLevel = areaInfo.getLevel()  # 当前行政区划级别 0-区域 1-省 2-市 3-县
			
			mxdCountyPath = os.path.join(mxdDir, pluginName, pluginName + "County.mxd")
			mxdCityPath = os.path.join(mxdDir, pluginName, pluginName + "City.mxd")
			mxdProvincePath = os.path.join(mxdDir, pluginName, pluginName + "Province.mxd")
			mxdNationPath = os.path.join(mxdDir, pluginName, pluginName + "Nation.mxd")
			
			if areaInfoLevel == 0:
				mxdList["County"] = mxdCountyPath
				mxdList["City"] = mxdCityPath
				mxdList["Province"] = mxdProvincePath
				mxdList["Nation"] = mxdNationPath
			elif areaInfoLevel == 1:
				mxdList["County"] = mxdCountyPath
				mxdList["City"] = mxdCityPath
				mxdList["Province"] = mxdProvincePath
			elif areaInfoLevel == 2:
				mxdList["County"] = mxdCountyPath
				mxdList["City"] = mxdCityPath
			elif areaInfoLevel == 3:
				mxdList["County"] = mxdCountyPath
			
			for mxdMark in mxdList:
				mxdPath = mxdList[mxdMark]
				if BaseFile.isFileOrDir(mxdPath) != BaseFile.ISFILE:
					continue
				exportMap = ArcPyUtil.exportJPEG(lyr_path_dict, ele_dict, mxdPath, outDir, rasterPath, mxdMark,
				                                 areaInfo, issue,
				                                 areaIDList, "")
				if exportMap != None:
					for exportKey in exportMap:
						returnPathMap[exportKey] = exportMap[exportKey]
			
			return returnPathMap
		except:
			return None
	
	@staticmethod
	def __changeTitleTxt(textElement, curName, issue, ele_dict):
		if textElement.name in ele_dict.keys():
			ElementReplaceVals = ele_dict[textElement.name]
			inTxt = textElement.text
			for replaceKey in ElementReplaceVals.keys():
				replaceVal = ElementReplaceVals[replaceKey]
				inTxt = inTxt.replace(replaceKey, replaceVal)
				textElement.text = inTxt
	
	@staticmethod
	def exportJPEG(lyr_path_dict, ele_dict, mxdPath, outDir, rasterPath, mxdMark, areaInfo, issue, areaIDList,
	               exFileName):
		flagExport = True
		returnPathMap = {}
		
		# 0数据准备
		lyr_info = {}
		for each_lyr in lyr_path_dict:
			each_lyr_path = lyr_path_dict[each_lyr]
			(lyr_file_folder, lyr_file_basename) = os.path.split(each_lyr_path)
			(lyr_file_name, lyr_file_extenction) = os.path.splitext(lyr_file_basename)
			lyr_info[each_lyr] = {"name": lyr_file_name, "extenction": lyr_file_extenction,
			                      "base_name": lyr_file_basename, "folder": lyr_file_folder}
		
		try:
			if StringFormat.isEmpty(exFileName):
				exFileName = ""
			
			# 1.修复图层
			mxd = arcpy.mapping.MapDocument(mxdPath)
			for lyr in arcpy.mapping.ListBrokenDataSources(mxd):
				if lyr.supports("DATASOURCE"):
					
					# 1.1 替换图层信息
					dstWorkspace = lyr_info[str(lyr)]["folder"]
					lyrRSName = lyr_info[str(lyr)]["name"]
					if lyr_info[str(lyr)]["extenction"] == ".shp":
						lyr.replaceDataSource(dstWorkspace, "SHAPEFILE_WORKSPACE", lyrRSName)
					if lyr_info[str(lyr)]["extenction"] == ".tif" or lyr_info[str(lyr)]["extenction"] == ".tiff" \
							or lyr_info[str(lyr)]["extenction"] == ".TIF" or lyr_info[str(lyr)]["extenction"] == ".TIFF" \
							or lyr_info[str(lyr)]["extenction"] == ".TIFF":
						lyr.replaceDataSource(dstWorkspace, "RASTER_WORKSPACE", lyrRSName)
				else:
					flagExport = False
					break
			
			if flagExport:
				print(mxdPath)
				print(mxd.dataDrivenPages.pageCount)
				for pageNum in range(1, mxd.dataDrivenPages.pageCount + 1):
					curName = ""
					curCode = ""
					curMxdLevel = 0
					mxd.dataDrivenPages.currentPageID = pageNum
					
					if mxdMark == "County":
						curName = mxd.dataDrivenPages.pageRow.name
						curCode = mxd.dataDrivenPages.pageRow.id
						curMxdLevel = 3
					elif mxdMark == "City":
						curName = mxd.dataDrivenPages.pageRow.name
						curCode = mxd.dataDrivenPages.pageRow.id
						curMxdLevel = 2
					elif mxdMark == "Province":
						curName = mxd.dataDrivenPages.pageRow.name
						curCode = mxd.dataDrivenPages.pageRow.id
						curMxdLevel = 1
					elif mxdMark == "Nation":
						curName = mxd.dataDrivenPages.pageRow.name
						curCode = mxd.dataDrivenPages.pageRow.id
						curMxdLevel = 0
					
					if str(curCode) not in areaIDList or not areaInfo.isSubChildID(str(curCode), curMxdLevel):
						continue
					
					# 修改标题
					for textElement in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):
						ArcPyUtil.__changeTitleTxt(textElement, curName, issue, ele_dict)
					
					# 获取文件名和路径
					BaseFile.creatDir(os.path.join(outDir, str(curCode)))
					regionPath = os.path.join(outDir, str(curCode) + "/" + str(curCode) + exFileName + ".jpg")
					if BaseFile.isFileOrDir(regionPath) == BaseFile.ISFILE:
						os.remove(regionPath)
					
					# 导出专题图
					arcpy.mapping.ExportToJPEG(mxd, regionPath, resolution=300)
					
					returnPathMap[str(curCode)] = regionPath
		
		except Exception as e:
			print(e)
			print(arcpy.GetMessages())
		finally:
			del mxd
			return returnPathMap
