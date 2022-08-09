# encoding: utf-8
"""
@author: DYX
@file: MainProcess.py
@time: 2020/10/14 15:09
@desc:
"""
from src.appSanQing.pluginsSanQing.MapFactory.MapFactory import MapFactory
from src.common.CartopyMapPy.Layout.entity.MapInfo import MapInfo


class MainProcess:
    """主要执行流程"""

    def __init__(self, cfg, tifFile, lyrFile, rgbPseudo, staMap, shpMark, shpFile, outDir, issueLabelText, Colors, ColorLevels,
                 ColorLabels):
        """cfg-配置信息实例"""
        self.__cfg = cfg
        self.__tifFile = tifFile
        self.__lyrFile = lyrFile
        self.__rgbPseudo = rgbPseudo
        self.__staMap = staMap
        self.__shpMark = shpMark
        self.__shpFile = shpFile
        self.__outDir = outDir
        self.__issueLabelText = issueLabelText
        self.__Colors = Colors
        self.__ColorLevels = ColorLevels
        self.__ColorLabels = ColorLabels

    def doProcess(self):
        """主流程控制"""
        plugainName = self.__cfg.getPlugainName()

        # 模板信息
        mapInfo = MapInfo(plugainName)
        mapInfo.AddLayoutInfotoMap(self.__cfg.getLayoutMap())
        mapInfo.AddPageSetupInfotoMap(self.__cfg.getPageCollectionMap())
        mapInfo.AddTitleInfoMap(self.__cfg.getTitleMap())
        mapInfo.AddAnnotationInfotoMap(self.__cfg.getAnnotationMap())
        mapInfo.AddPictureInfotoMap(self.__cfg.getPictureMap())
        mapInfo.AddLabelInfotoMap(self.__cfg.getLabelMap())
        mapInfo.AddIssueInfotoMap(self.__cfg.getIssueMap())
        mapInfo.AddAtlasInfotoMap(self.__cfg.getAtlasMap())
        mapInfo.AddDataFrameInfotoMap(self.__cfg.getDataFrameMap())
        mapInfo.AddMapGridInfotoMap(self.__cfg.getDataFrameMap())
        mapInfo.AddScaleBarInfotoMap(self.__cfg.getScaleBarMap())
        mapInfo.AddNorthArrowInfotoMap(self.__cfg.getNorthArrowMap())
        mapInfo.AddtifFiletoMap(self.__tifFile)
        mapInfo.AddlyrOverlytoMap(self.__lyrFile, self.__cfg.getRastersMap())
        mapInfo.AddRGBFileMaptoMap(self.__rgbPseudo, self.__cfg.getRGBMap())
        mapInfo.AddstaMaptoMap(self.__staMap)
        mapInfo.AddshpFiletoMap(self.__shpFile)
        mapInfo.AddshpMarktoMap(self.__shpMark)
        mapInfo.AddoutDirtoMap(self.__outDir)
        mapInfo.AddissueLabelTexttoMap(self.__issueLabelText)

        # Productxml信息
        mapInfo.AddColorstoMap(self.__Colors)
        mapInfo.AddColorLevelstoMap(self.__ColorLevels)
        mapInfo.AddColorLabelstoMap(self.__ColorLabels)

        mapFactoryIns = MapFactory()
        mapObj = mapFactoryIns.getPlugin(mapInfo)
        if mapObj is None:
            return
        try:
            flag = mapObj.doMap()
            if flag:
                returnMapPath = mapObj.returnJPGMap, mapObj.returnPNGMap
                return returnMapPath
            else:
                return None
        except:
            return
