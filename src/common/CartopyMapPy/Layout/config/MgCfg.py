# encoding: utf-8
"""
@author: DYX
@file: MgCfg.py
@time: 2020/10/14 11:46
@desc:
"""

from src.common.CartopyMapPy.Layout.config.CfgXML import TemplateTXML


class MgCfg:
    """系统配置信息管理器"""

    def __init__(self, plugainName, templatePath):
        self.__plugainName = plugainName

        # 模板信息获取
        self.__TemplateCfg = TemplateTXML(templatePath)

    def loadCfgInfo(self):
        """加载专题模板信息"""
        self.__TemplateCfg.loadTemplate()

    def getPlugainName(self):
        return self.__plugainName

    def getTemplateCfg(self):
        return self.__TemplateCfg

    def getLayoutMap(self):
        return self.__TemplateCfg.cfgInfoMap['Layout']

    def getPageCollectionMap(self):
        return self.__TemplateCfg.cfgInfoMap['PageCollection']

    def getTitleMap(self):
        return self.__TemplateCfg.cfgInfoMap['Title']

    def getAnnotationMap(self):
        return self.__TemplateCfg.cfgInfoMap['Annotation']

    def getPictureMap(self):
        return self.__TemplateCfg.cfgInfoMap['Picture']

    def getLabelMap(self):
        return self.__TemplateCfg.cfgInfoMap['Label']

    def getIssueMap(self):
        return self.__TemplateCfg.cfgInfoMap['Issue']

    def getRastersMap(self):
        return self.__TemplateCfg.cfgInfoMap['Rasters']

    def getRGBMap(self):
        return self.__TemplateCfg.cfgInfoMap['RGB']

    def getAtlasMap(self):
        return self.__TemplateCfg.cfgInfoMap['Atlas']

    def getDataFrameMap(self):
        return self.__TemplateCfg.cfgInfoMap['DataFrame']

    def getScaleBarMap(self):
        return self.__TemplateCfg.cfgInfoMap['ScaleBar']

    def getNorthArrowMap(self):
        return self.__TemplateCfg.cfgInfoMap['NorthArrow']
