# -- coding: utf-8 --

import os 

from src.common.config.ConstParam import ConstParam
from src.common.config.CfgBase import CfgBase
from src.common.config.CfgProduct import CfgProduct
from src.common.config.CfgArea import CfgArea
from src.common.utils.FileUtil import BaseFile
from src.common.entity.DBInfo import DBInfo
from src.common.jdbc.DBFactory import DBFactory


class MgCfg:
    """系统配置信息管理器基类 不同的应用配置管理器如果读取配置信息不同 在其应用下继承该MgCfg重写子类"""
    
    def __init__(self, rootDir):
        """rootDir 项目根目录"""  
        # 异常日志目录 不是产品算法的日志信息目录
        self.__rootDir = rootDir
        self.__logFolder = os.path.join(rootDir, "Log") 
        BaseFile.creatDir(self.__logFolder)
        
        # 依赖项配置信息 
        self.__dependCfg = CfgBase(os.path.join(rootDir, "depend/DependCfg.properties"))
        self.loadDependCfgInfo()
         
        # 系统配置信息实例
        dependCfgDir = os.path.join(self.__dependCfg.cfgInfoMap[ConstParam.DEPENDFOLDER], "config")
        self.__sysCfg = CfgBase(os.path.join(dependCfgDir, "SysCfg.properties"))
        self.__areaCfg = CfgArea(os.path.join(dependCfgDir, "AreaCfg.xml"))
        self.__productCfg = CfgProduct(os.path.join(dependCfgDir, "ProductCfg.xml"))

        # 数据库实例
        self.__dbIns = None 
         
         
    def loadDependCfgInfo(self): 
        """加载依赖项信息 配置目录未获取到赋空串信息 不影响后续执行"""        
        self.__dependCfg.loadCfgInfo(False, "", False, self.__rootDir)
        if not ConstParam.DEPENDFOLDER in self.__dependCfg.cfgInfoMap.keys():
            self.__dependCfg.cfgInfoMap[ConstParam.DEPENDFOLDER] = "" 
        if not ConstParam.IDLAPPFOLDER in self.__dependCfg.cfgInfoMap.keys():
            self.__dependCfg.cfgInfoMap[ConstParam.IDLAPPFOLDER] = "" 
            

    def loadCfgOthersInfo(self):
        """待子类覆盖"""
        pass
    
    
    def loadCfgInfo(self):
        """加载配置信息及初始化数据库操作实例"""   
        # 【1】读取SysCfg.properties文件
        self.__sysCfg.loadCfgInfo(False, "", False)
        
        # 【2】读取产品配置信息
        APIUrl = self.__sysCfg.cfgInfoMap['APIUrl']
        self.__productCfg.loadCfgInfo(True, "Plugin", False, url=APIUrl)
        
        # 【3】读取行政区划配置信息
        if ConstParam.TOPAREAID in self.__sysCfg.cfgInfoMap.keys():
            topAreaID = self.__sysCfg.cfgInfoMap[ConstParam.TOPAREAID]
            self.__areaCfg.setTopID(topAreaID)
            self.__areaCfg.loadCfgInfo(True, "Area", True)
            
        # 【4】初始化数据库实例 
        if ConstParam.DBTYPE in self.__sysCfg.cfgInfoMap.keys() \
            and ConstParam.DBURL in self.__sysCfg.cfgInfoMap.keys()\
            and ConstParam.DBUser in self.__sysCfg.cfgInfoMap.keys()\
            and ConstParam.DBPswd in self.__sysCfg.cfgInfoMap.keys()\
            and ConstParam.DBName in self.__sysCfg.cfgInfoMap.keys():
            dbType = self.__sysCfg.cfgInfoMap[ConstParam.DBTYPE]
            dbURL = self.__sysCfg.cfgInfoMap[ConstParam.DBURL]
            dbUser = self.__sysCfg.cfgInfoMap[ConstParam.DBUser]
            dbPswd = self.__sysCfg.cfgInfoMap[ConstParam.DBPswd]
            dbName = self.__sysCfg.cfgInfoMap[ConstParam.DBName]
            if dbType != None and dbURL != None:
                dbInfo = DBInfo(dbType, dbURL, dbUser, dbPswd, dbName) 
                DBFactory.getInstance().setDBInfo(dbInfo)
                self.__dbIns = DBFactory.getInstance().getDBObj() 
 
    
    def getLogFolder(self):
        """返回异常日志目录"""
        return self.__logFolder 
    
    def getDependCfg(self):
        """返回依赖项配置信息"""
        return self.__dependCfg 
    
    def getSysCfg(self):
        """返回系统配置信息"""
        return self.__sysCfg 
    
    def getProductCfg(self):
        """返回产品配置信息"""
        return self.__productCfg 
    
    def getDBIns(self):
        """返回数据库实例"""
        return self.__dbIns

    def getRootAreaInfo(self):
        """获取顶级行政区划配置信息"""
        if ConstParam.TOPAREAID in self.__sysCfg.cfgInfoMap.keys():
            topAreaID = self.__sysCfg.cfgInfoMap[ConstParam.TOPAREAID]
            if topAreaID in self.__areaCfg.cfgInfoMap.keys():
                return self.__areaCfg.cfgInfoMap[topAreaID]
        return None