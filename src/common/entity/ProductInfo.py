# -- coding: utf-8 --
import os

from src.common.config.ConstParam import ConstParam
from src.common.utils.FileUtil import BaseFile
from src.common.utils.StringFormat import StringFormat


class ProductInfo:
    """产品算法信息(全过程信息) 产品名称/描述信息/正则表达式/超时时间-分钟/算法路径/输入参数信息/输出信息"""

    def __init__(self, pluginName, prodDesp, fileFilter, outTimeMin, idlExePath, FillValue="-999"):

        # 算法配置信息
        self.__pluginName = pluginName
        self.__prodDesp = prodDesp
        self.__fileFilter = fileFilter
        self.__outTimeMin = outTimeMin
        self.__idlExePath = idlExePath

        self.__reMapAry = {}
        self.__reMapAryNew = {}
        self.__reMapColorLevels = []
        self.__reMapColorLevelsNew = {}
        self.__reMapColors = []
        self.__reMapColorsNew = {}
        self.__reMapColorLabels = []
        self.__reMapColorLabelsNew = {}

        self.__count = 0
        self.__ReMapList = [{}]
        self.__countV = 0
        self.__ReMapListV = [[]]
        self.__countC = 0
        self.__ReMapListC = [[]]
        self.__countL = 0
        self.__ReMapListL = [[]]
        self.__FillValue = FillValue

        # 算法输入信息
        self.__areaID = ""
        self.__issue = ""
        self.__cycle = ""
        self.__inputFile = ""
        self.__outFolder = ""
        self.__outXMLPath = ""
        self.__outLogPath = ""
        self.__dependFolder = ""
        self.__idlAppFolder = ""
        self.__tempFolder = ""

        self.__dependMap = {}
        self.__inputXMLMap = {}
        self.__outXMLMap = {}

        self.__curAreaInfo = None
        self.__cfgMgInstance = None
        self.__daoInstance = None

        # 初始化__outXMLMap信息
        self.__initOutXMLMap()

    def __initOutXMLMap(self):
        # regions下包含所有行政区划的输出文件信息（每个行政区划一个region节点） mosaicFiles为镶嵌数据集过滤名称
        # tables下包含所有需要入库的信息（每张表一个table节点）
        self.__outXMLMap["log"] = {"status": "2", "info": "Failed"}
        self.__outXMLMap["outFiles"] = {"regions": {}, "extents": {}, "geoserverFiles": []}
        self.__outXMLMap["tables"] = {}

    def addReMapAry(self, minV, maxV, reV):
        minV = StringFormat.strToFloat(minV)
        maxV = StringFormat.strToFloat(maxV)
        rmV = StringFormat.strToInt(reV)
        if (minV is None) or (maxV is None) or (rmV is None):
            return
        reKey = "VALUE >= " + str(minV) + " and " + "VALUE < " + str(maxV)
        if not (reKey in self.__reMapAry.keys()):
            self.__reMapAry[reKey] = rmV

    def addReMapAryNew(self, minV, maxV, reV, TYPE, item):
        if item > self.__count:
            self.__count += 1
            self.__ReMapList.append({})

        minV = StringFormat.strToFloat(minV)
        maxV = StringFormat.strToFloat(maxV)
        rmV = StringFormat.strToInt(reV)
        if (minV is None) or (maxV is None) or (rmV is None):
            return
        reKey = "VALUE >= " + str(minV) + " and " + "VALUE < " + str(maxV)
        if not (reKey in self.__ReMapList[item].keys()):
            # self.__tmpreMapAry[reKey] = rmV
            self.__ReMapList[item][reKey] = rmV
        self.__reMapAryNew[TYPE] = self.__ReMapList[item]

    def addReMapMinMaxV(self, minV, maxV):
        if minV is None or maxV is None:
            return

        minV = StringFormat.strToFloat(minV)
        maxV = StringFormat.strToFloat(maxV)

        self.__reMapColorLevels.append(minV)
        self.__reMapColorLevels.append(maxV)
        self.__reMapColorLevels = list(set(self.__reMapColorLevels))
        self.__reMapColorLevels.sort()

    def addReMapMinMaxVNew(self, minV, maxV, TYPE, item):
        if item > self.__countV:
            self.__countV += 1
            self.__ReMapListV.append([])

        if minV is None or maxV is None:
            return

        minV = StringFormat.strToFloat(minV)
        maxV = StringFormat.strToFloat(maxV)

        self.__ReMapListV[item].append(minV)
        self.__ReMapListV[item].append(maxV)
        self.__ReMapListV[item] = list(set(self.__ReMapListV[item]))
        self.__ReMapListV[item].sort()

        self.__reMapColorLevelsNew[TYPE] = self.__ReMapListV[item]

    def addReMapColor(self, color):
        if color is None:
            return
        self.__reMapColors.append(color)

    def addReMapColorNew(self, color, TYPE, item):
        if item > self.__countC:
            self.__countC += 1
            self.__ReMapListC.append([])

        if color is None:
            return
        self.__ReMapListC[item].append(color)

        self.__reMapColorsNew[TYPE] = self.__ReMapListC[item]

    def addReMapLabel(self, label):
        if label is None:
            return
        self.__reMapColorLabels.append(label)

    def addReMapLabelNew(self, label, TYPE, item):
        if item > self.__countL:
            self.__countL += 1
            self.__ReMapListL.append([])

        if label is None:
            return
        self.__ReMapListL[item].append(label)

        self.__reMapColorLabelsNew[TYPE] = self.__ReMapListL[item]

    def getPluginName(self):
        return self.__pluginName

    def getProdDesp(self):
        return self.__prodDesp

    def getFileFilter(self):
        return self.__fileFilter

    def getFillValue(self):
        return self.__FillValue

    def getReMapAry(self):
        # key-分级条件（字符串） value-分级值（整形）
        return self.__reMapAry

    def getReMapAryNew(self, TYPE):
        return self.__reMapAryNew[TYPE]

    def getColorLevels(self):
        return self.__reMapColorLevels

    def getColorLevelsNew(self, TYPE):
        return self.__reMapColorLevelsNew[TYPE]

    def getColors(self):
        return self.__reMapColors

    def getColorsNew(self, TYPE):
        return self.__reMapColorsNew[TYPE]

    def getColorLabels(self):
        return self.__reMapColorLabels

    def getColorLabelsNew(self, TYPE):
        return self.__reMapColorLabelsNew[TYPE]

    def getOutTimeMin(self):
        return self.__outTimeMin

    def getOutTimeSecd(self):
        return self.__outTimeMin * 60

    def getIdlExePath(self):
        return self.__idlExePath

    def getInputXMLMap(self):
        return self.__inputXMLMap

    def getOutXMLMap(self):
        return self.__outXMLMap

    def getAreaID(self):
        return self.__areaID

    def getIssue(self):
        return self.__issue

    def getCycle(self):
        return self.__cycle

    def getInputFile(self):
        return self.__inputFile

    def getOutFolder(self):
        return self.__outFolder

    def getOutXMLPath(self):
        return self.__outXMLPath

    def getOutLogPath(self):
        return self.__outLogPath

    def getDependFolder(self):
        return self.__dependFolder

    def getIDLAppFolder(self):
        return self.__idlAppFolder

    def getTempFolder(self):
        return self.__tempFolder

    def getCurAreaInfo(self):
        return self.__curAreaInfo

    def getCfgMgInstance(self):
        return self.__cfgMgInstance

    def getDaoInstance(self):
        return self.__daoInstance

    def addAllInfoToDependMap(self, dependMap):
        for dependKey in dependMap.keys():
            self.__dependMap[dependKey] = dependMap[dependKey]

    def getInputInfoByKey(self, inputKey):
        if inputKey in self.__inputXMLMap.keys():
            return self.__inputXMLMap[inputKey]
        else:
            return None

    def addInfoToInputMap(self, inputKey, inputValue):
        if inputKey in self.__inputXMLMap.keys():
            return
        self.__inputXMLMap[inputKey] = inputValue

    def addAllInfoToInputMap(self, inputMap):
        for inputKey in inputMap.keys():
            self.__inputXMLMap[inputKey] = inputMap[inputKey]

    def updateOutXMLlog(self, status, info):
        self.__outXMLMap["log"]["status"] = status
        self.__outXMLMap["log"]["info"] = info

    def addOutXMLGeoserverFiles(self, geoserverFileList):
        # geoserverFileList结构 [{"type":"", "file":""}]
        geoserverFiles = self.__outXMLMap["outFiles"]["geoserverFiles"]
        for geoserverFile in geoserverFileList:
            geoserverFiles.append(geoserverFile)

    def addAllOutXMLRegionFiles(self, regionMap):
        # regionMap[regionID]=region regionID-区域编号 region结构 [{"type":"", "file":""}]
        for regionID in regionMap.keys():
            self.addSgOutXMLFiles(regionID, regionMap[regionID])

    def addSgOutXMLFiles(self, regionID, region):
        # regionID-区域编号 region结构 [{"type":"", "file":""}]
        regions = self.__outXMLMap["outFiles"]["regions"]
        if regionID in regions.keys():
            return
        regions[regionID] = region

    def addAllOutXMLExtenMaps(self, extentMap):
        # extenMap结构[AreaID] = {'xmin':'', 'xmax':'', 'ymin':'', 'ymax':''}
        extents = self.__outXMLMap["outFiles"]['extents']
        for regionID in extentMap.keys():
            if regionID in extents.keys():
                return
            extents[regionID] = extentMap[regionID]

    def addOutXMLOutTables(self, tableName, tableValue):
        # tableName-表名 tableValue结构 {"field":"","values":[]}
        tables = self.__outXMLMap["tables"]
        if tableName in tables.keys():
            return
        tables[tableName] = tableValue

    def addAllOutXMLOutTables(self, tableMap):
        # tableMap[tableName]=tableValue tableName-表名 tableValue结构 {"field":"","values":[]}
        for tableName in tableMap.keys():
            self.addOutXMLOutTables(tableName, tableMap[tableName])

    def getALLAreaIDList(self, curAreaInfo):
        """获取整个AreaInfo的ID号"""

        curAreaID = curAreaInfo.getAreaID()

        areaIDList = []
        areaIDList.append(curAreaID)  # Level 1

        Level2IDList = curAreaInfo.getAreaIDList()
        areaIDList.extend(Level2IDList)  # Level 2

        for Lev2AreaID in Level2IDList:
            Lev2AreaInfo = curAreaInfo.getAreaByID(Lev2AreaID)
            Level3IDList = Lev2AreaInfo.getAreaIDList()  # Level 3
            areaIDList.extend(Level3IDList)

            for Lev3AreaID in Level3IDList:
                Lev3AreaInfo = curAreaInfo.getAreaByID(Lev3AreaID)
                Level4IDList = Lev3AreaInfo.getAreaIDList()  # Level4

                if Level4IDList is None:
                    continue
                else:
                    areaIDList.extend(Level4IDList)

        return areaIDList

    def isActive(self, cfgMgIns):
        # 只检测行政区划、产品期次、产品周期、输入文件、输出目录、输出xml路径和输出日志路径
        # 这些信息在xml配置项里字段定义是固定的 不能改变
        if not (ConstParam.AREAID in self.__inputXMLMap.keys()) or not (ConstParam.ISSUE in self.__inputXMLMap.keys()) \
                or not (ConstParam.INPUTFILE in self.__inputXMLMap.keys()) or not (
                ConstParam.OUTFOLDER in self.__inputXMLMap.keys()) \
                or not (ConstParam.OUTXMLPATH in self.__inputXMLMap.keys()) or not (
                ConstParam.OUTLOGPATH in self.__inputXMLMap.keys()) \
                or not (ConstParam.CYCLE in self.__inputXMLMap.keys()):
            return False

        tempFolder = cfgMgIns.getSysCfg().getCfgInfoByKey(ConstParam.TEMPFOLDER)
        if StringFormat.isEmpty(tempFolder):
            return False

        areaID = self.__inputXMLMap[ConstParam.AREAID]
        issue = self.__inputXMLMap[ConstParam.ISSUE]
        cycle = self.__inputXMLMap[ConstParam.CYCLE]
        inputFile = self.__inputXMLMap[ConstParam.INPUTFILE]
        outFolder = self.__inputXMLMap[ConstParam.OUTFOLDER]
        outXMLPath = self.__inputXMLMap[ConstParam.OUTXMLPATH]
        outLogPath = self.__inputXMLMap[ConstParam.OUTLOGPATH]

        curArea = None
        rootArarInfo = cfgMgIns.getRootAreaInfo()
        if rootArarInfo is None:
            return False
        if rootArarInfo.getAreaID() == areaID:
            curArea = rootArarInfo
        else:
            curArea = rootArarInfo.getAreaByID(areaID)
            if curArea is None:
                return False

        if StringFormat.isEmpty(issue) or StringFormat.isEmpty(cycle) or StringFormat.isEmpty(inputFile) \
                or StringFormat.isEmpty(outFolder) or StringFormat.isEmpty(outXMLPath) or StringFormat.isEmpty(
            outLogPath):
            return False

        if not (ConstParam.DEPENDFOLDER in self.__dependMap.keys()) \
                or not (ConstParam.IDLAPPFOLDER in self.__dependMap.keys()):
            return False
        dependFolder = self.__dependMap[ConstParam.DEPENDFOLDER]
        idlAppFolder = self.__dependMap[ConstParam.IDLAPPFOLDER]
        if BaseFile.isFileOrDir(dependFolder) != BaseFile.ISDIR or BaseFile.isFileOrDir(idlAppFolder) != BaseFile.ISDIR:
            return False

        self.__areaID = areaID
        self.__issue = issue
        self.__cycle = cycle
        self.__inputFile = inputFile
        self.__outFolder = outFolder
        self.__outXMLPath = outXMLPath
        self.__outLogPath = outLogPath
        self.__dependFolder = dependFolder
        self.__idlAppFolder = idlAppFolder
        self.__curAreaInfo = curArea
        self.__cfgMgInstance = cfgMgIns
        self.__daoInstance = cfgMgIns.getDBIns()
        self.__tempFolder = tempFolder

        BaseFile.creatDir(self.__tempFolder)
        BaseFile.creatDir(os.path.dirname(self.__outLogPath))
        BaseFile.creatDir(os.path.dirname(self.__outXMLPath))

        print("areaID:", self.__areaID)
        print("issue:", self.__issue)
        print("PluginName:", self.getPluginName())
        print("OutFolder", self.__outFolder)
        return True
