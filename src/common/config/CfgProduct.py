# -- coding: utf-8 --
import os
import xml.dom.minidom
from xml.dom.minidom import parseString
import numpy as np
import requests
from src.common.config.CfgBase import CfgBase
from src.common.config.ConstParam import ConstParam
from src.common.utils.StringFormat import StringFormat
from src.common.entity.ProductInfo import ProductInfo
from src.common.utils.FileUtil import BaseFile


class CfgProduct(CfgBase):
    """产品算法配置信息读取"""

    def __init__(self, filePath):
        CfgBase.__init__(self, filePath)

    def loadCfgInfo(self, isXML=True, nodeName="", isRoot=False, rootDir="", url=""):
        """加载配置信息 XML或properties配置信息"""
        if BaseFile.isFileOrDir(self.filePath) != BaseFile.ISFILE:
            return
        if isXML and StringFormat.isEmpty(nodeName):
            return
        try:
            self.cfgInfoMap = {}
            # 【1】读取 xml 文件
            if isXML:
                # 在读取xml之前先从url中获取相应信息
                urlstr = self.getAPIUrl(url)
                # if urlstr['code'] == "200" or urlstr['code'] == 200:  # 当从code==200，则从api接口中获取ProductCfg信息
                #     domTree = parseString(urlstr['content'])
                # else:  # 否则，从本地文件中获取ProductCfg信息
                #     domTree = xml.dom.minidom.parse(self.filePath)
                domTree = xml.dom.minidom.parse(self.filePath)  # 本地测试，将该行代码放开
                rootNode = domTree.documentElement
                if isRoot:
                    self.getRootXMLInfo(rootNode)
                else:
                    secondNodes = rootNode.getElementsByTagName(nodeName)
                    for secondNode in secondNodes:
                        self.getSecondRootXMLInfo(secondNode)
        except Exception as e:
            print(e)

    def getAPIUrl(self, url):
        try:
            req = requests.get(url, timeout=3.0)
            req_json = req.json()
            return req_json
        except Exception as e:
            print(e)
            return

    def getSecondRootXMLInfo(self, secondNode):
        """从二级节点下获取产品配置信息"""

        try:
            if not secondNode.hasAttribute(ConstParam.PLUGINNAME):
                return

            pluginName = secondNode.getAttribute(ConstParam.PLUGINNAME).strip()
            if pluginName in self.cfgInfoMap.keys():
                return

            prodDespNode = self.getElements(secondNode, ConstParam.PRODDESP)
            filterNode = self.getElements(secondNode, ConstParam.FILEFILTER)
            outTimeMinNode = self.getElements(secondNode, ConstParam.OUTTIMEMIN)
            idlExePathNode = self.getElements(secondNode, ConstParam.IDLEXEPATH)
            reMapNode = self.getElements(secondNode, ConstParam.REMAP)

            # FIXME 获取无效值信息，放到字典里面去
            FillValue = reMapNode[0].getAttribute(ConstParam.FILLVALUE).strip()
            if prodDespNode == None or filterNode == None or reMapNode == None or outTimeMinNode == None or idlExePathNode == None:
                return

            # "childNodes"就不检测了
            prodDesp = prodDespNode[0].childNodes[0].data.strip()
            fileFilter = filterNode[0].childNodes[0].data.strip()
            outTimeMin = outTimeMinNode[0].childNodes[0].data.strip()
            idlExePath = idlExePathNode[0].childNodes[0].data.strip()

            if StringFormat.isEmpty(idlExePath):
                return
            if not StringFormat.isStrToNumber(outTimeMin, True):
                outTimeMin = ConstParam.MINOUTTIME
            else:
                outTimeMin = StringFormat.strToInt(outTimeMin)
                if outTimeMin < ConstParam.MINOUTTIME:
                    outTimeMin = ConstParam.MINOUTTIME
                elif outTimeMin > ConstParam.MAXOUTTIME:
                    outTimeMin = ConstParam.MAXOUTTIME

            # productInfo = ProductInfo(pluginName, prodDesp, fileFilter, outTimeMin, idlExePath)
            productInfo = ProductInfo(pluginName, prodDesp, fileFilter, outTimeMin, idlExePath, FillValue)
            self.cfgInfoMap[pluginName] = productInfo

            for item in np.arange(len(reMapNode)):
                nextNodes = reMapNode[item].childNodes
                for curNode in nextNodes:
                    try:
                        if curNode.hasAttribute("MinV") and curNode.hasAttribute("MaxV") and curNode.hasAttribute("ReV") \
                                and curNode.hasAttribute("Color") and curNode.hasAttribute("Label"):
                            minV = curNode.getAttribute("MinV").strip()
                            maxV = curNode.getAttribute("MaxV").strip()
                            reV = curNode.getAttribute("ReV").strip()

                            color = curNode.getAttribute("Color").strip()
                            label = curNode.getAttribute("Label").strip()

                            if len(reMapNode) == 1:
                                productInfo.addReMapAry(minV, maxV, reV)
                                productInfo.addReMapMinMaxV(minV, maxV)
                                productInfo.addReMapColor(color)
                                productInfo.addReMapLabel(label)
                            else:
                                TYPE = reMapNode[item].getAttribute(ConstParam.TYPE).strip()
                                productInfo.addReMapAryNew(minV, maxV, reV, TYPE, item)
                                productInfo.addReMapMinMaxVNew(minV, maxV, TYPE, item)
                                productInfo.addReMapColorNew(color, TYPE, item)
                                productInfo.addReMapLabelNew(label, TYPE, item)

                    except:
                        pass
        except Exception as e:
            print(e)
