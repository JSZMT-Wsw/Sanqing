# -- coding: utf-8 --  

import json
import os
import time

import numpy as np
import shapefile
from osgeo import gdal

from src.common.CartopyMapPy.Layout.MapPy import MapPy
from src.common.config.ConstParam import ConstParam
from src.common.utils.FileUtil import BaseFile
from src.common.utils.GeoProcessUtil import GeoProcessUtil
from src.common.utils.SysUtil import SysUtil
from src.common.utils.SysUtil import TimeoutError


# reload(sys)
# sys.setdefaultencoding('utf-8')  # 注意中文字符


class BaseProcess:
    """产品处理基类"""

    def __init__(self, pluginParam):
        """pluginParam - ProductInfo 产品算法全过程信息"""
        self.name = pluginParam.getPluginName()
        self.pluginParam = pluginParam
        self.curAreaInfo = pluginParam.getCurAreaInfo()  # 当前行政区划信息
        self.daoIns = pluginParam.getDaoInstance()  # 数据库操作实例
        self.cfgMgIns = pluginParam.getCfgMgInstance()  # 配置实例
        self.logPath = pluginParam.getOutLogPath()  # 日志路径

        self.processType = 3  # 处理类型 1-只执行算法处理 2-只执行统计分析 3-执行算法处理后进行统计分析（默认类型）
        self.processOther = False  # 是否执行其它处理操作
        self.rsOutMap = {}  # 算法输出文件列表信息 文件标识+文件路径

        t = time.time()
        self.milsecondStr = str(int(round(t * 1000)))  # 当前时间毫秒数

        self.curProdFolder = ""  # 当前产品根目录
        tpFolder = pluginParam.getTempFolder()  # 临时目录根目录
        self.tempFolder_root = tpFolder  # 临时目录根目录
        self.tempFolder = os.path.join(tpFolder, self.milsecondStr)  # 当前临时目录
        BaseFile.creatDir(self.tempFolder)

        sysCfg = pluginParam.getCfgMgInstance().getSysCfg()
        self.GeoserverFolder = sysCfg.getCfgInfoByKey(ConstParam.GEOSERVERFolder)  # geoserver 根目录
        self.curGeoserverFolder = ""  # 当前geoserver目录

        # 按照行政区划输出的文件信息 结构[AreaID]= [{"type":"", "file":[]}]
        self.outFileMap = {}
        # 输出的统计信息 结构[TableName]= [{"field":"", "values":[]}]
        self.outStaMap = {}
        # 区域四至边界(纯色图四至范围一致) 结构[AreaID] = {'xmin':'', 'xmax':'', 'ymin':'', 'ymax':''}
        self.outExtentMap = {}

        self.isOutExe = True  # true-外部可执行处理程序 false-内部python模块

        self.shpMap = {}  # 矢量路径

        self.lyrFile = {}  # 叠加单通道文件信息
        self.rgbFile = {}   # 叠加RGB三通道文件信息

        # 初始化资源
        self.doInit()

        self.type = ""
        # 该内容在一个插件对应多个色标的情况下使用，且必须在对应插件中写，不能在基类中更改
        # 为了获取不同时次(频次)ProductCfg.xml中的信息，需要InputXML中提供一个关键字，并补全“xx”
        # self.type = self.pluginParam.getInputInfoByKey("xx")

        BaseFile.appendLogInfo(self.logPath, "0%", "-------------------------------------------------")

    def doInit(self):
        """初始化资源"""
        # 如果self.processType = 2 输入的待处理信息需要存储至self.rsOutMap,
        # 产品目录  默认时间到月份 时间/期次_周期/行政区划/
        issue = self.pluginParam.getIssue()
        cycle = self.pluginParam.getCycle()
        issueTime = issue[0:6]
        self.curProdFolder = os.path.join(self.pluginParam.getOutFolder(), self.name,
                                          issueTime + "/" + issue + "_" + cycle)
        BaseFile.creatDir(self.curProdFolder)
        # --------------------------------------------

        self.curGeoserverFolder = self.GeoserverFolder + "/" + self.name.lower() + "_" + cycle.lower()
        BaseFile.creatDir(self.curGeoserverFolder)
        # --------------------------------------------

        dependDic = self.pluginParam.getDependFolder()
        compShpDir = os.path.join(dependDic, "CompShp")
        countyShp = os.path.join(compShpDir, "AreaCounty.shp")
        cityShp = os.path.join(compShpDir, "AreaCity.shp")
        provinceShp = os.path.join(compShpDir, "AreaProvince.shp")
        regionShp = os.path.join(compShpDir, "AreaNation.shp")

        self.shpMap["County"] = countyShp
        self.shpMap["City"] = cityShp
        self.shpMap["Province"] = provinceShp
        self.shpMap["Nation"] = regionShp
        # --------------------------------------------

        self.getExtentMapInfo()

    def getExtentMapInfo(self):
        """获取各个行政区划下的四至边界信息"""

        extentMapInfo = self.outExtentMap

        for shpPath in self.shpMap.values():
            if BaseFile.isFileOrDir(shpPath) != BaseFile.ISFILE:
                continue
            sf = shapefile.Reader(shpPath)  # encoding='gb18030'
            for i in range(len(sf.shapes())):
                curID = sf.record(i).ID
                bbox = sf.shape(i).bbox  # 第i个shape类的 左下角 Lon,Lat  +   右上角 Lon,Lat
                extentMapInfo[curID] = {'xmin': bbox[0], 'xmax': bbox[2], 'ymin': bbox[1], 'ymax': bbox[3]}

    def doProcess(self):
        """执行处理入口"""
        flagProcess = False

        if self.processType == 1:
            flagProcess = self.doRSExecute()
        if self.processType == 2:
            flagProcess = self.doStatis(1)
        if self.processType == 3:
            flagProcess = self.doRSExecute()
            if flagProcess:
                flagProcess = self.doStatis(30)
        # 额外操作
        if self.processOther:
            flagProcess = self.doOthers()

        self.doDispose()  # 释放资源

        # 写入 xml 信息
        if flagProcess:
            self.pluginParam.updateOutXMLlog(ConstParam.STATESUCESS, "Success!")
            self.pluginParam.addAllOutXMLRegionFiles(self.outFileMap)
            self.pluginParam.addAllOutXMLExtenMaps(self.outExtentMap)
            self.pluginParam.addAllOutXMLOutTables(self.outStaMap)
            BaseFile.appendLogInfo(self.logPath, "100%", "执行完毕 成功")
        else:
            self.pluginParam.updateOutXMLlog(ConstParam.STATEFAILED, "Failed!")
            BaseFile.appendLogInfo(self.logPath, "100%", "执行完毕 失败")

        BaseFile.writeOutXML(self.pluginParam.getOutXMLPath(), self.name, self.pluginParam.getOutXMLMap())

        return flagProcess

    # 执行算法计算部分------------------------------------

    def doRSExecute(self):
        """执行算法处理 算法输出存储至self.rsOutMap"""
        self.rsOutMap = {}

        if self.isOutExe:
            cmdStr = self.getRSCmdInfo()

            if cmdStr is None:
                return False
            try:
                BaseFile.appendLogInfo(self.logPath, "1%", "开始进行算法处理...")
                SysUtil.doCmd(cmdStr, timeOutSeconds=self.pluginParam.getOutTimeSecd())
            except TimeoutError as e:
                BaseFile.appendLogInfo(self.logPath, "90%", e)
                return False

        else:
            self.doInnerPy()

        return self.checkRSResult()

    def getRSCmdInfo(self):
        """获取算法cmd字符串 必须重写"""
        return None

    def doInnerPy(self):
        """执行内部的py模块时必须重写 算法输出存储至self.rsOutMap"""
        pass

    def checkRSResult(self):
        """算法执行结果检测"""
        if len(self.rsOutMap) == 0:
            return False
        flagRS = True
        for outPath in self.rsOutMap.values():
            if BaseFile.isFileOrDir(outPath) != BaseFile.ISFILE:
                flagRS = False
                break

            BaseFile.appendLogInfo(self.logPath, "30%", "算法执行成功-" + outPath)
        return flagRS

    def doStatis(self, proNumber):
        """统计分析"""
        dependDic = self.pluginParam.getDependFolder()
        compShpDir = os.path.join(dependDic, "CompShp")
        countyShp = os.path.join(compShpDir, "AreaCounty.shp")
        cityShp = os.path.join(compShpDir, "AreaCity.shp")
        provinceShp = os.path.join(compShpDir, "AreaProvince.shp")
        regionShp = os.path.join(compShpDir, "AreaNation.shp")

        if BaseFile.isFileOrDir(countyShp) != BaseFile.ISFILE:
            countyShp = None
        if BaseFile.isFileOrDir(cityShp) != BaseFile.ISFILE:
            cityShp = None
        if BaseFile.isFileOrDir(provinceShp) != BaseFile.ISFILE:
            provinceShp = None
        if BaseFile.isFileOrDir(regionShp) != BaseFile.ISFILE:
            regionShp = None

        BaseFile.appendLogInfo(self.logPath, str(proNumber) + "%", "开始执行统计分析...")
        if countyShp == None and cityShp == None and provinceShp == None and regionShp == None:
            BaseFile.appendLogInfo(self.logPath, "90%", "处理失败 shp文件配置路径异常")
            return False

        flagRt = False

        perStep = (100 - proNumber) / (len(self.rsOutMap))
        curProNumber = proNumber
        for rsKey in self.rsOutMap.keys():
            # 遍历输出文件进行处理
            tifPath = self.rsOutMap[rsKey]
            # 获取 统计信息 裁切 生成专题图
            BaseFile.appendLogInfo(self.logPath, str(curProNumber) + "%", "分析文件-" + tifPath)
            flagOK = self.doStatisComp(self.tempFolder, tifPath, curProNumber)
            if not flagRt and flagOK:
                flagRt = True

            curProNumber = curProNumber + perStep

        return flagRt

    def doStatisComp(self, tempDir, tifPath, curProNumber):
        """统计分析"""



        staMap = self.dostaMapInit(tifPath)

        # #【1】统计，【临时文件夹，tif文件，最小的行政区划，区域的等级】，无需返回值
        # ConstParam.NORMALSTATISTICS（正常统计）, ConstParam.GRADATIONSTATISTICS（分级统计）, ConstParam.ALLSTATISTICS（分级统计 + 正常统计）
        self.areaStatis(tempDir, tifPath, ConstParam.ALLSTATISTICS)

        # 【2】专题图
        curProNumber = curProNumber + 10
        self.creatPic(tifPath, staMap, str(float('%.2f' % curProNumber)))

        # 【3】裁切
        curProNumber = curProNumber + 10
        self.areaClipTif(tifPath, staMap, str(float('%.2f' % curProNumber)))

        # 【4】报告
        # curProNumber = curProNumber + 2
        # self.exportWord(self, tifPath, staMap, str(float('%.2f' % curProNumber)))

        return True

    def dostaMapInit(self, tifPath):
        """执行统计、裁剪、出专题图前的区域判定"""
        fillValue = float(self.pluginParam.getFillValue())
        areaIDList = GeoProcessUtil.SpatialGeometry(tifPath, self.shpMap, fillValue)

        Nan = ['Nan'] * len(areaIDList)
        staMap = dict(zip(areaIDList, Nan))

        return staMap

    # 执行统计计算部分------------------------------------

    def areaStatis(self, tempDir, tifPath, mode=ConstParam.ALLSTATISTICS):
        """统计分析"""
        conditionSta = self.getStaCondition()
        conditionStaRe = self.getStaConditionRe()

        fillValue = float(self.pluginParam.getFillValue())

        staMap = {}  # 正常统计结果
        staMapRe = {}  # 分级统计结果

        if mode == ConstParam.NORMALSTATISTICS or mode == ConstParam.ALLSTATISTICS:
            # 【1】正常统计
            dataLists = GeoProcessUtil.NormalStastic(tifPath, self.shpMap, conditionSta, fillValue)

            if dataLists != None:
                for key in dataLists.keys():
                    staRow = dataLists[key]
                    staMap[key] = staRow

            print("常规统计完成")
            BaseFile.appendLogInfo(self.logPath, str(34) + "%", "常规统计完成")

        if mode == ConstParam.GRADATIONSTATISTICS or mode == ConstParam.ALLSTATISTICS:
            # 【2】分级统计
            remapAry = self.pluginParam.getReMapAry()
            if len(remapAry.keys()) == 0:
                remapAry = self.pluginParam.getReMapAryNew(self.type)
            for remapKey in remapAry.keys():
                remapValue = str(remapAry[remapKey])
                dataListsRe = GeoProcessUtil.GradationStastic(tempDir, tifPath, self.shpMap, remapKey)

                if dataListsRe != None:
                    for key in dataListsRe.keys():
                        staRow = dataListsRe[key]
                        if not (key in staMapRe.keys()):
                            staMapRe[key] = {}
                        staMapRe[key][remapValue] = staRow
            print("分级统计完成")
            BaseFile.appendLogInfo(self.logPath, str(38) + "%", "分级统计完成")

        # 【3】更新数据
        if mode == ConstParam.GRADATIONSTATISTICS:
            self.updateStaMapInfo({"StaMapRe": staMapRe})
        elif mode == ConstParam.NORMALSTATISTICS:
            self.updateStaMapInfo({"StaMap": staMap})
        elif mode == ConstParam.ALLSTATISTICS:
            self.updateStaMapInfo({"StaMapRe": staMapRe, "StaMap": staMap})
        print("统计信息写入XML完成")
        BaseFile.appendLogInfo(self.logPath, str(40) + "%", "统计信息写入XML完成")

    def getStaCondition(self):
        """算法执行结果检测 正常统计的必须重写"""
        return ["MAX", "MEAN", "MIN"]

    def getStaConditionRe(self):
        """算法执行结果检测 分级统计的必须重写"""
        return ["Count"]

    def updateStaMapInfo(self, staMapInfo):
        """
        更新统计信息 必须覆盖 staMap结构 [AreaID]=row 从索引1处开始与统计条件对应 信息更新至self.outStaMap中
        """
        pass

    # 执行专题图制作部分------------------------------------
    def creatPic(self, tifPath, staMap, curProInfo):
        """生成专题图 """
        returnJPGMap = {}
        returnPNGMap = {}

        BaseFile.appendLogInfo(self.logPath, curProInfo, "生成专题图...")

        dependDic = self.pluginParam.getDependFolder()
        TemplateDic = dependDic + "/" + "Template"

        issueLabelText = self.pluginParam.getIssue()

        Colors = self.pluginParam.getColors()
        if len(Colors) == 0:
            Colors = self.pluginParam.getColorsNew(self.type)
        ColorLevels = self.pluginParam.getColorLevels()
        if len(ColorLevels) == 0:
            ColorLevels = self.pluginParam.getColorLevelsNew(self.type)
        ColorLabels = self.pluginParam.getColorLabels()
        if len(ColorLabels) == 0:
            ColorLabels = self.pluginParam.getColorLabelsNew(self.type)

        for shpMark in self.shpMap:
            shpPath = self.shpMap[shpMark]
            if BaseFile.isFileOrDir(shpPath) != BaseFile.ISFILE:
                continue

            templatePath = TemplateDic + "/" + self.name + "/" + self.name + shpMark + ".xml"
            if BaseFile.isFileOrDir(templatePath) != BaseFile.ISFILE:
                continue

            returnMapPath = MapPy(tifPath, self.lyrFile, self.rgbFile, staMap, shpMark, shpPath, self.curProdFolder, self.name,
                                  issueLabelText, Colors, ColorLevels, ColorLabels, templatePath)

            if returnMapPath is None:
                return

            JPGMap = returnMapPath[0]
            PNGMap = returnMapPath[1]
            returnJPGMap.update(JPGMap)
            returnPNGMap.update(PNGMap)

        if len(returnJPGMap.keys()) == 0 and len(returnPNGMap.keys()) == 0:
            return False

        for areaID in returnJPGMap.keys():
            suffix = BaseFile.getFilePathInfo(returnJPGMap[areaID], True)[2]
            if areaID in self.outFileMap.keys():
                self.outFileMap[areaID].append({"type": suffix, "file": returnJPGMap[areaID]})
            else:
                self.outFileMap[areaID] = []
                self.outFileMap[areaID].append({"type": suffix, "file": returnJPGMap[areaID]})

        for areaID in returnPNGMap.keys():
            suffix = BaseFile.getFilePathInfo(returnPNGMap[areaID], True)[2]
            if areaID in self.outFileMap:
                self.outFileMap[areaID].append({"type": suffix, "file": returnPNGMap[areaID]})
            else:
                self.outFileMap[areaID] = []
                self.outFileMap[areaID].append({"type": suffix, "file": returnPNGMap[areaID]})

        print("专题图生产完成")
        BaseFile.appendLogInfo(self.logPath, str(float(curProInfo) + 10) + "%", "专题图生产完成...")

    # 执行栅格裁剪部分------------------------------------
    def areaClipTif(self, tifPath, staMap, curProInfo):
        """按照行政区划裁切"""
        BaseFile.appendLogInfo(self.logPath, curProInfo, "执行行政区划裁切...")

        clipDir = os.path.join(self.pluginParam.getDependFolder(), "SubShp")
        for areaID in staMap.keys():
            outClipPath = self.doClipSrcTif(tifPath, clipDir, areaID, os.path.join(self.curProdFolder, areaID))
            if outClipPath != None:
                # 按照行政区划输出的文件信息 结构[AreaID]= [{"type":"", "file":[]}]
                # self.outFileMap[areaID] = [{"type":".tif", "file":outClipPath}]
                if areaID in self.outFileMap:
                    self.outFileMap[areaID].append({"type": ".tif", "file": outClipPath})
                else:
                    self.outFileMap[areaID] = []
                    self.outFileMap[areaID].append({"type": ".tif", "file": outClipPath})

        print("裁剪完成")
        BaseFile.appendLogInfo(self.logPath, str(float(curProInfo) + 10) + "%", "裁剪完成")

    def doClipSrcTif(self, tifPath, clipDir, areaID, dirOut):
        '''各个行政区划裁切'''
        try:
            fileShp = os.path.join(clipDir, areaID + ".shp")
            outClipPath = GeoProcessUtil.clip_by_shp(tifPath, fileShp, dirOut + "/" + areaID + ".tif")
            # self.doTiftoJSON(outClipPath, areaID, dirOut)

            TopAreaID = self.cfgMgIns._MgCfg__sysCfg.cfgInfoMap['TopAreaID']
            if areaID == TopAreaID:
                issue = self.pluginParam.getIssue()
                _ = self.name + '_' + self.pluginParam.getCycle()
                targetName = _.lower() + issue[0:8] + "T" + issue[8:12] + "00000Z" + ".tif"
                BaseFile.copyFileByName(outClipPath, self.curGeoserverFolder, targetName)

                # 更新产品
                self.pluginParam.addOutXMLGeoserverFiles(
                    [{"type": ".tif", "file": os.path.join(self.curGeoserverFolder, targetName)}])

            return outClipPath
        except:
            return None

    def doTiftoJSON(self, outclipTif, areaID, dirOut):
        """tif转json"""
        try:
            ds = gdal.Open(outclipTif)
            XSize = ds.RasterXSize
            YSize = ds.RasterYSize
            nodata = ds.GetRasterBand(1).GetNoDataValue()

            # 计算重采样系数并重采样
            if max(XSize, YSize) < 500:
                scale = 1.0
            else:
                scale = max(XSize, YSize) / 500.0
            XSize = XSize / scale
            YSize = YSize / scale
            resds = gdal.Warp("", ds, format="MEM", width=XSize, height=YSize, resampleAlg=gdal.GRA_Bilinear)
            data, XSize, YSize, geotrans, proj = GeoProcessUtil.read_tiff(resds, 1)
            idx = np.where(data == nodata)
            lonMin = geotrans[0]
            latMin = geotrans[3] + geotrans[5] * YSize
            lonMax = geotrans[0] + geotrans[1] * XSize
            latMax = geotrans[3]
            dLon = lonMax - lonMin
            dLat = latMax - latMin

            # 采样后数据处理
            data[idx] = np.nan
            valueMin, valueMax = np.float(np.nanmin(data)), np.float(np.nanmax(data))
            valueMean = np.nanmean(data)
            if valueMean < 1:
                valueScale = 1000
            elif 1 <= valueMean < 10:
                valueScale = 100
            else:
                valueScale = 1
            data = (data * valueScale).astype(int)
            data[idx] = -999
            data = data.tolist()

            # json数据准备
            # lonMin latMin lonNums latNums dLon dLat valueScale valueMin valueMax 1
            Bound = [lonMin, latMin, XSize, YSize, dLon, dLat, valueScale, valueMin, valueMax, 1, [1000]]
            DataAry = []
            for item in range(YSize):
                DataAry.extend(data[-1 + item])
            jsonDict = {
                "Bound": Bound,
                "DataAry": DataAry,
            }
            jsonFile = dirOut + "/" + areaID + ".json"
            with open(jsonFile, "w") as f:
                f.write(json.dumps(jsonDict))

            if BaseFile.isFileOrDir(jsonFile) == BaseFile.ISFILE:
                # 按照行政区划输出的文件信息 结构[AreaID]= [{"type":"", "file":[]}]
                # self.outFileMap[areaID] = [{"type":".tif", "file":outClipPath}]
                if areaID in self.outFileMap:
                    self.outFileMap[areaID].append({"type": "CLOUDCTT", "file": jsonFile})
                else:
                    self.outFileMap[areaID] = []
                    self.outFileMap[areaID].append({"type": "CLOUDCTT", "file": jsonFile})
        except Exception as e:
            print(e)
            return None

    # 执行word报告生成部分------------------------------------
    def exportWord(self, tifPath, staMap, curProInfo):
        """生成统计报告 """
        BaseFile.appendLogInfo(self.logPath, curProInfo, "生成统计报告...")

    # 主流程后续操作------------------------------------

    def doOthers(self):
        """执行其它处理"""
        return False

    def doDispose(self):
        """释放资源"""
        BaseFile.appendLogInfo(self.logPath, str(90) + "%", "删除临时文件")
        BaseFile.removeDir(self.tempFolder)

    def checkRemapAry(self):
        '''根据需要由子类覆盖 检测配置的统计分类信息'''
        remapAry = self.pluginParam.getReMapAry()
        if len(remapAry) > 0:
            return True
        else:
            return False
