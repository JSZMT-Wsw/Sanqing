# encoding: utf-8
"""
@author: DYX
@file: CfgXML.py
@time: 2020/10/14 11:45
@desc:
"""

import os
import xml.dom.minidom

import numpy as np


class TemplateTXML:
    """xml解析"""

    def __init__(self, filePath):
        self.filePath = filePath  # 文件路径
        self.cfgInfoMap = {}  # 信息字典 结构 [String] = Obj

    def loadTemplate(self):
        """模板信息读取"""
        if os.path.exists(self.filePath) == False:
            return

        try:
            domTree = xml.dom.minidom.parse(self.filePath)
            rootNode = domTree.documentElement

            # Layout  属性
            LayoutInfo = self.loadLayoutAttri(rootNode)
            self.cfgInfoMap['Layout'] = LayoutInfo

            # PageCollection 节点信息
            PageCollectionMap = self.loadPageCollectionInfo(rootNode)
            self.cfgInfoMap['PageCollection'] = PageCollectionMap

            # LayoutItem 节点信息
            self.cfgInfoMap['Issue'] = {}
            self.cfgInfoMap['Title'] = {}
            self.cfgInfoMap['Annotation'] = {}
            self.cfgInfoMap['Picture'] = {}
            self.cfgInfoMap['Label'] = {}
            self.cfgInfoMap['Rasters'] = {}
            self.cfgInfoMap['RGB'] = {}
            self.cfgInfoMap['Atlas'] = {}
            self.cfgInfoMap['ScaleBar'] = {}
            self.cfgInfoMap['NorthArrow'] = {}
            self.loadLayoutItemInfo(rootNode)
        except:
            print("Template xml Prase Faild")

    def loadLayoutAttri(self, rootNode):
        """获取Layout节点信息"""
        try:
            LayoutInfo = {}

            for key in rootNode.attributes.keys():
                attr = rootNode.attributes[key]
                LayoutInfo[attr.name] = attr.value

            return LayoutInfo
        except:
            return

    def loadPageCollectionInfo(self, rootNode):
        """获取PageCollection节点下的信息"""
        try:
            PageCollectionInfo = {}

            PageCollectionNodes = rootNode.getElementsByTagName('PageCollection')[0]
            LayoutItemNodes = PageCollectionNodes.getElementsByTagName('LayoutItem')

            # LayoutItem节点属性
            for LayoutItemNode in LayoutItemNodes:
                if LayoutItemNode.nodeType == 3:
                    continue
                for key in LayoutItemNode.attributes.keys():
                    attr = LayoutItemNode.attributes[key]
                    PageCollectionInfo[attr.name] = attr.value

            # LayoutItem下属节点
            childNodes = LayoutItemNodes[0].childNodes

            # LayoutItem下属节点的对应属性
            for childNode in childNodes:
                if childNode.nodeName != "#text":
                    PageCollectionInfo[childNode.nodeName] = {}

                    for key in childNode.attributes.keys():
                        attr = childNode.attributes[key]
                        PageCollectionInfo[childNode.nodeName][attr.name] = attr.value

            return PageCollectionInfo
        except:
            return

    def loadLayoutItemInfo(self, rootNode):
        """获取LayoutItem节点信息"""
        AnnotationConst = 0
        PictureConst = 0
        LabelConst = 0
        RastersConst = 0
        AtlasConst = 0
        ScaleBarConst = 0
        NorthArrowConst = 0

        LayoutItemNodes = rootNode.getElementsByTagName("LayoutItem")
        for LayoutItemNode in LayoutItemNodes:
            if LayoutItemNode.hasAttribute("type"):
                type = LayoutItemNode.getAttribute('type')

                if type == 'PageSetup':
                    continue

                elif type == "DataFrame":
                    DataFrameInfo = self.loadDataFramInfo(LayoutItemNode)
                    self.cfgInfoMap['DataFrame'] = DataFrameInfo

                elif type == "Title":
                    TitleInfo = self.loadNodeInfo(LayoutItemNode, 0)
                    self.cfgInfoMap[type] = TitleInfo[0]

                elif type == "Annotation":
                    AnnotationInfo = self.loadNodeInfo(LayoutItemNode, AnnotationConst)
                    self.cfgInfoMap[type].update(AnnotationInfo)
                    AnnotationConst += 1

                elif type == "Picture":
                    PictureInfo = self.loadNodeInfo(LayoutItemNode, PictureConst)
                    self.cfgInfoMap[type].update(PictureInfo)
                    PictureConst += 1

                elif type == "Label":
                    TextInfo = self.loadNodeInfo(LayoutItemNode, LabelConst)
                    self.cfgInfoMap[type].update(TextInfo)
                    LabelConst += 1

                elif type == "Issue":
                    IssueInfo = self.loadNodeInfo(LayoutItemNode, 0)
                    self.cfgInfoMap[type] = IssueInfo[0]

                elif type == "Rasters":
                    RastersInfo = self.loadNodeInfo(LayoutItemNode, RastersConst)
                    self.cfgInfoMap[type].update(RastersInfo)
                    RastersConst += 1

                elif type == "RGB":
                    RGBInfo = self.loadNodeInfo(LayoutItemNode, 0)
                    self.cfgInfoMap[type].update(RGBInfo)

                elif type == "Atlas":
                    AtlasInfo = self.loadNodeInfo(LayoutItemNode, AtlasConst)
                    self.cfgInfoMap[type].update(AtlasInfo)
                    AtlasConst += 1

                elif type == 'ScaleBar':
                    ScaleBarInfo = self.loadNodeInfo(LayoutItemNode, ScaleBarConst)
                    self.cfgInfoMap[type].update(ScaleBarInfo)
                    ScaleBarConst += 1

                elif type == 'NorthArrow':
                    NorthArrowInfo = self.loadNodeInfo(LayoutItemNode, NorthArrowConst)
                    self.cfgInfoMap[type].update(NorthArrowInfo)
                    NorthArrowConst += 1

    def loadDataFramInfo(self, LayoutItemNode):
        """获取DataFrame下的节点信息"""
        try:
            DataFrameInfo = {}

            # DataFrame 节点属性
            for key in LayoutItemNode.attributes.keys():
                attr = LayoutItemNode.attributes[key]
                DataFrameInfo[attr.name] = attr.value

            # FrameColor BackgroundColor Extent ComposerMapGrid 节点
            for child in LayoutItemNode.childNodes:
                if child.nodeType == 3:  # 3为文本类型
                    continue

                # FrameColor 和 BackgroundColor  节点属性
                if child.nodeName == 'FrameColor' or child.nodeName == 'BackgroundColor':
                    red = child.getAttribute('red')
                    green = child.getAttribute('green')
                    blue = child.getAttribute('blue')
                    alpha = child.getAttribute('alpha')
                    DataFrameInfo[child.nodeName] = [red, green, blue, alpha]
                    continue

                # Extent ComposerMapGrid 节点属性
                DataFrameInfo[child.nodeName] = {}
                for key in child.attributes.keys():
                    attr = child.attributes[key]
                    DataFrameInfo[child.nodeName][attr.name] = attr.value

                # ComposerMapGrid 下的  lineStyle markerStyle annotationFontProperties节点
                for lastChild in child.childNodes:
                    if lastChild.nodeType == 3:
                        continue

                    # 节点属性
                    DataFrameInfo[child.nodeName][lastChild.nodeName] = {}
                    for key in lastChild.attributes.keys():
                        attr = lastChild.attributes[key]
                        DataFrameInfo[child.nodeName][lastChild.nodeName][attr.name] = attr.value

            return DataFrameInfo
        except:
            print('DataFrame节点获取失败')
            return

    def loadNodeInfo(self, node, Const):
        """Annotation， Picture， Label， Atlas节点信息读取"""
        try:
            nodeInfo = {}
            nodeInfo[Const] = {}

            # node节点下的属性
            for key in node.attributes.keys():
                attr = node.attributes[key]
                nodeInfo[Const][attr.name] = attr.value

            # node下一级节点
            childNodes = node.childNodes

            # 遍历node下属节点 获取各个节点下的属性
            for childNode in childNodes:
                if childNode.nodeName != "#text":  # 不为text的节点
                    nodeInfo[Const][childNode.nodeName] = {}

                    for key in childNode.attributes.keys():
                        attr = childNode.attributes[key]
                        nodeInfo[Const][childNode.nodeName][attr.name] = attr.value

                    # 遍历节点下面的值
                    nodes = childNode.getElementsByTagName('ReMap')
                    if len(nodes) > 0:
                        colorList = []
                        labelList = []
                        levelList = []
                        for curNode in nodes:
                            try:
                                if curNode.hasAttribute("MinV") and curNode.hasAttribute(
                                        "MaxV") and curNode.hasAttribute("ReV") \
                                        and curNode.hasAttribute("Color") and curNode.hasAttribute("Label"):
                                    minV = float(curNode.getAttribute("MinV").strip())
                                    maxV = float(curNode.getAttribute("MaxV").strip())

                                    color = curNode.getAttribute("Color").strip()
                                    label = curNode.getAttribute("Label").strip()

                                    colorList.append(color)
                                    labelList.append(label)

                                    levelList.append(minV)
                                    levelList.append(maxV)
                                    levelList = list(set(levelList))
                                    levelList.sort()
                            except:
                                pass
                        nodeInfo[Const][childNode.nodeName]['Rev'] = levelList
                        nodeInfo[Const][childNode.nodeName]['Color'] = colorList
                        nodeInfo[Const][childNode.nodeName]['Label'] = labelList

            return nodeInfo
        except:
            type = node.getAttribute('type')
            print(type + "节点信息获取失败")
            return
