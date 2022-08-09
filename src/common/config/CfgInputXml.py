# -*- coding:utf-8 -*-
 
from src.common.config.CfgBase import CfgBase
from src.common.config.ConstParam import ConstParam

class CfgInputXml(CfgBase):
    """算法配置信息读取"""

    def __init__(self, filePath):
        CfgBase.__init__(self, filePath) 
        
        
    def getRootXMLInfo(self, rootNode):
        """从一级节点下获取算法标识（名称）信息"""
        
        try:
            if not(rootNode.hasAttribute("identify")):
                return
            pluginName = rootNode.getAttribute("identify").strip() 
            self.cfgInfoMap[ConstParam.PLUGINNAME] = pluginName
            
            secondNodes = rootNode.childNodes
            for secondNode in secondNodes:
                try:
                    if secondNode.hasAttribute("identify"):
                        inputKey = secondNode.getAttribute("identify").strip()
                        inputvalue = secondNode.childNodes[0].data.strip()
                        if not(inputKey in self.cfgInfoMap.keys()):
                            self.cfgInfoMap[inputKey] = inputvalue 
                except : 
                    pass 
        except Exception as e:
            print(e)



 

