# -- coding: utf-8 --

import os
import datetime
import shutil

from src.common.utils.StringFormat import StringFormat
from xml.dom.minidom import Document 


class BaseFile:
    """文件基础操作类"""

    def __init__(self):
        pass

    ISOTHER = 0
    ISDIR = 1
    ISFILE = 2
    ISALL = 3

    LOGINFO = "INFO"
    LOGWARN = "WARN"
    LOGERROR = "ERROR"
        
        
    @staticmethod
    def getParentRootPath():  
        """获取当前执行文件的上一级目录路径"""
        curPath = os.path.abspath(os.path.dirname(__file__))  
        return os.path.split(curPath)[0]
        
        
    @staticmethod
    def isFileOrDir(filePath):  
        """文件或文件夹检测 路径不存在返回ISOTHER"""
        if StringFormat.isEmpty(filePath):
            return BaseFile.ISOTHER        
        if os.path.exists(filePath):
            if os.path.isfile(filePath):
                return BaseFile.ISFILE
            else:
                return BaseFile.ISDIR
        else:
            return BaseFile.ISOTHER
            
            
    @staticmethod
    def creatDir(dirPath):  
        """创建文件夹"""
        if StringFormat.isEmpty(dirPath):
            return False         
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
            return True
        else:
            return True
    
    
    @staticmethod
    def removeDir(dirPath):  
        """删除文件夹 文件被占用是删除不掉的"""
        try:
            if BaseFile.isFileOrDir(dirPath) != BaseFile.ISDIR:
                return
            shutil.rmtree(dirPath) 
        except:
            pass
            
            
    @staticmethod
    def getFileList(dirPath, fileType):  
        """获取指定目录下的文件或目录列表 fileType=1-目录 2-文件 3-目录和文件"""
        if BaseFile.isFileOrDir(dirPath) != BaseFile.ISDIR:
            return None        
        ary = []
        for fileName in os.listdir(dirPath):
            filePath = os.path.join(dirPath, fileName) 
            if fileType == BaseFile.ISALL or\
                (fileType == BaseFile.ISDIR and os.path.isdir(filePath)) or\
                (fileType == BaseFile.ISFILE and os.path.isfile(filePath)):
                ary.append(filePath)           
        return ary    
            
                    
    @staticmethod
    def getFilePathInfo(filePath, isExist):  
        """获取文件的文件夹/文件名/后缀名 isExist-文件是否已经存在"""
        if StringFormat.isEmpty(filePath):
            return None         
        if not os.path.exists(filePath) and isExist:
            return None
        else:
            ary1 = os.path.split(filePath)
            ary2 = os.path.splitext(ary1[1])
            return ary1[0], ary2[0], ary2[1]
        
        
    @staticmethod
    def readTxtFileStr(filePath):
        """读取文本文件内容"""
        if BaseFile.isFileOrDir(filePath) != BaseFile.ISFILE:
            return None
        with open(filePath, 'r') as f:
            reMap = f.read()
            return reMap
        
                    
    @staticmethod
    def copyFile(sourceFile, targetDir):  
        """拷贝文件 以原文件名称拷贝"""
        if BaseFile.isFileOrDir(sourceFile) != BaseFile.ISFILE:
            return False        
        ary1 = os.path.split(sourceFile) 
        return BaseFile.copyFileByName(sourceFile, targetDir, ary1[1])
        
           
    @staticmethod
    def copyFileByName(sourceFile, targetDir, targetName):  
        """拷贝文件 以指定文件名称拷贝"""
        if BaseFile.isFileOrDir(sourceFile) != BaseFile.ISFILE or StringFormat.isEmpty(targetDir) or StringFormat.isEmpty(targetName):
            return False        
        targetFile = os.path.join(targetDir, targetName)        
        if not os.path.exists(targetDir):
            os.makedirs(targetDir)        
        try:
            if not os.path.exists(targetFile) or(os.path.exists(targetFile) and (os.path.getsize(targetFile) != os.path.getsize(sourceFile))):
                with open(targetFile, "wb") as ft:
                    with open(sourceFile, "rb") as fs:
                        ft.write(fs.read())
            return True        
        except Exception as e:
            print(e)
            return False
        
    
    @staticmethod
    def reNameFile(sourceFile, newFileName):  
        """文件重命名"""
        if BaseFile.isFileOrDir(sourceFile) != BaseFile.ISFILE or StringFormat.isEmpty(newFileName):
            return False

        ary = BaseFile.getFilePathInfo(sourceFile, True)
        if ary is None:
            return False
        try:
            os.rename(sourceFile, os.path.join(ary[0], newFileName))
            return True
        except Exception as e:
            print(e)
            return False


    @staticmethod
    def appendLogInfo(logFile, logLevel, logInfo):
        """写文本日志(追加方式) 文件绝对路径/进度信息或日志等级/信息
        input:
            logfile:    log文件路径
            logLevel:   进度信息或日志等级
            logInfo:    log信息            
        """
        if StringFormat.isEmpty(logFile) or StringFormat.isEmpty(logLevel) or StringFormat.isEmpty(logInfo):
            return
        timeNow = datetime.datetime.now()
        timeNowstr = StringFormat.dateToStr(timeNow, "", False) 
        with open(logFile, 'a') as f:
            f.write(logLevel + "\t" + timeNowstr + "\t" + logInfo + "\n")
             

    @staticmethod
    def addSubNode(document, curNode, nodeKey, nodeValue, nodeAtt={}):
        """在节点下添加子节点信息"""
        try:  
            child = document.createElement(nodeKey)
            # 写属性
            for attKey in nodeAtt:
                child.setAttribute(attKey, nodeAtt[attKey])
            # 写值
            if nodeValue:
                child_text = document.createTextNode(nodeValue)
                child.appendChild(child_text)
            # 添加节点
            curNode.appendChild(child) 
        except :
            pass
            
            
    @staticmethod
    def writeOutXML(xmlPath, pluginName, outXMLMap):
        """存储产品输出XML信息 pluginName-算法标识 outXMLMap-产品输出信息对象（字典结构，信息尽量屏蔽中文及转义字符）"""
        # outXMLMap结构定义见 ProductInfo/__outXMLMap
        try:                      
            logMap = outXMLMap["log"]
            outputFilesMap = outXMLMap["outFiles"]
            regionMap = outputFilesMap["regions"]
            extentMap = outputFilesMap["extents"]
            mosaicFiles = outputFilesMap["geoserverFiles"]
            tablesMap = outXMLMap["tables"]
               
            document = Document()
            
            # 创建根节点
            rootElement = document.createElement('xml')
            rootElement.setAttribute('identify', pluginName)
            document.appendChild(rootElement)
             
            # 创建log节点  logMap = {"status":"", "info":""}
            logElement = document.createElement('log')
            rootElement.appendChild(logElement)
            for logKey in logMap.keys():
                BaseFile.addSubNode(document, logElement, logKey, logMap[logKey])
             
            # 创建outputFiles节点 outputFilesMap["outputFiles"] = {"regions":{}, "mosaicFiles":[]}
            outFilesElement = document.createElement('outFiles')
            rootElement.appendChild(outFilesElement)
            
            # regionMap[regionID] = [{"type":"", "file":""}]
            for regionKey in regionMap.keys():
                regionElement = document.createElement('region')
                regionElement.setAttribute('identify', regionKey)
                if regionKey in extentMap.keys():
                    for extentkey in extentMap[regionKey].keys():
                        regionElement.setAttribute(extentkey, str(extentMap[regionKey][extentkey]))
                outFilesElement.appendChild(regionElement) 
                for region in regionMap[regionKey]:
                    BaseFile.addSubNode(document, regionElement, 'file', region['file'], {'type':region['type']})
                    
            # geoserverFileList = [{"type":"", "file":""}]
            mosaicElement = document.createElement('geoserverFile')
            outFilesElement.appendChild(mosaicElement)
            for mosaicFile in mosaicFiles: 
                BaseFile.addSubNode(document, mosaicElement, 'file', mosaicFile['file'], {'type':mosaicFile['type']})
            
            # 创建tables节点 tablesMap[tableName] = {"field":"","values":[]}  
            tablesElement = document.createElement('tables')
            rootElement.appendChild(tablesElement)
            for tableKey in tablesMap.keys():
                tableElement = document.createElement('table')
                tableElement.setAttribute('identify', tableKey)
                tablesElement.appendChild(tableElement) 
                
                fieldInfo = tablesMap[tableKey]['field']
                BaseFile.addSubNode(document, tableElement, 'field', fieldInfo)
                
                valuesList = tablesMap[tableKey]['values'] 
                for tableValue in valuesList:
                    BaseFile.addSubNode(document, tableElement, 'values', tableValue)  
            
            # 存储 xml信息
            with open(xmlPath, 'wb') as f:
                f.write(document.toprettyxml(indent='\t', encoding='utf-8'))
        except Exception as e:
            print(e)
               
            
            
            
            
            
            
