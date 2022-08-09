# -- coding: utf-8 -- 
import os
import xml.dom.minidom 
from src.common.utils.FileUtil import BaseFile
from src.common.utils.StringFormat import StringFormat

    
class CfgBase:
    """配置信息基类"""
        
    def __init__(self, filePath):
        self.filePath = filePath  # 文件路径
        self.cfgInfoMap = {}  # 信息字典 结构 [String] = Obj
        
         
    def loadCfgInfo(self, isXML=True, nodeName="", isRoot=False, rootDir=""):
        """加载配置信息 XML或properties配置信息"""        
        if BaseFile.isFileOrDir(self.filePath) != BaseFile.ISFILE:
            return
        if isXML and StringFormat.isEmpty(nodeName):
            return
        try:
            self.cfgInfoMap = {}
            # 【1】读取 xml 文件
            if isXML:
                domTree = xml.dom.minidom.parse(self.filePath) 
                rootNode = domTree.documentElement 
                if isRoot:
                    self.getRootXMLInfo(rootNode)
                else:                    
                    secondNodes = rootNode.getElementsByTagName(nodeName)
                    for secondNode in secondNodes:
                        self.getSecondRootXMLInfo(secondNode)
            # 【2】读取配置文件
            else:
                fopen = open(self.filePath, 'r')
                for line in fopen:
                    line = line.strip()
                    if line.find('=') > 0 and not line.startswith('#'):
                        strs = line.split('=')
                        if rootDir == "":
                            self.cfgInfoMap[strs[0].strip()] = strs[1].strip()
                        else:
                            self.cfgInfoMap[strs[0].strip()] = os.path.join(rootDir, strs[1].strip())
                fopen.close() 
        except Exception as e:
            print(e)
    
    
    def getElements(self, curNode, elementName):
        """获取XML节点信息"""
        nodes = curNode.getElementsByTagName(elementName) 
        if len(nodes) == 0:
            return None
        else:
            return nodes
        
            
    def getRootXMLInfo(self, rootNode):
        """从一级节点下获取信息"""
        pass
    
    
    def getSecondRootXMLInfo(self, secondNode):
        """从二级节点下获取信息"""
        pass
    
     
    def getCfgInfoMap(self):
        """获取配置信息 """
        return self.cfgInfoMap
    
    
    def getCfgInfoByKey(self, cfgKey):
        """根据标识获取指定配置信息"""
        if cfgKey in self.cfgInfoMap.keys(): 
            return self.cfgInfoMap[cfgKey]
        return None
 
  
    
     
  
      


           
      
            

        
