# -- coding: utf-8 --
    
from src.common.config.CfgBase import CfgBase
from src.common.utils.StringFormat import StringFormat
from src.common.entity.AreaInfo import AreaInfo

 
class CfgArea(CfgBase):
    """行政区划配置信息读取"""

    def __init__(self, filePath): 
        CfgBase.__init__(self, filePath)
        self.topID = None
      
      
    def setTopID(self, topID):
        self.topID = topID
    
    
    def getRootXMLInfo(self, rootNode):
        """从一级节点下获取根节点行政区划信息"""

        try:
            if not(rootNode.hasAttribute("id") and rootNode.hasAttribute("name")):
                return
            areaID = rootNode.getAttribute("id").strip()
            if areaID != self.topID:
                return

            areaName = rootNode.getAttribute("name").strip()
            if StringFormat.isEmpty(areaName):
                return

            areaLevel = rootNode.getAttribute("level").strip()
            if not StringFormat.isStrToNumber(areaLevel, True):
                return

            rootArea = AreaInfo(areaID, areaName, StringFormat.strToInt(areaLevel), "100000000")
            self.cfgInfoMap[areaID] = rootArea

            secondNodes = rootNode.childNodes
            for secondNode in secondNodes:
                secondArea = self.__getNextNode(secondNode, areaID)
                if not(secondArea is None):
                    rootArea.addArea(secondArea)
        except Exception as e:
            print(e)
    
    
    def __getNextNode(self, node, dirID):
        """递归获取获取行政区划信息"""

        try:
            if not(node.hasAttribute("id") and node.hasAttribute("name")):
                return None

            areaID = node.getAttribute("id").strip()
            areaName = node.getAttribute("name").strip()
            areaLevel = node.getAttribute("level").strip()
            if StringFormat.isEmpty(areaID) or StringFormat.isEmpty(areaName) or not StringFormat.isStrToNumber(areaLevel, True):
                return None

            areaInfo = AreaInfo(areaID, areaName, StringFormat.strToInt(areaLevel), dirID)

            nextNodes = node.childNodes
            for secondNode in nextNodes:
                areaNext = self.__getNextNode(secondNode, areaID)
                if not(areaNext is None):
                    areaInfo.addArea(areaNext)

            return areaInfo
        except : 
            return None