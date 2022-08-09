# encoding: utf-8
"""
@author: DYX
@file: MapInfo.py
@time: 2020/10/15 14:14
@desc:
"""
import os
import numpy as np


class MapInfo:
    """xml 执行过程中的全信息"""

    def __init__(self, plugainName):
        self.__plugainName = plugainName

        # Layout属性
        self.__printResolution = ""
        self.__drivenPages = ""
        self.__Margin = ""

        # PageSetup 信息
        self.__PageSetup = {}
        # Title 信息
        self.__Title = {}
        # Annotation 信息
        self.__Annotation = {}
        # AddPicture 信息
        self.__Picture = {}
        # Label 信息
        self.__Label = {}
        # Issue 信息
        self.__Issue = {}
        # Altas 信息
        self.__Atlas = {}
        # DataFrame信息
        self.__DataFrame = {}
        # MapGrid信息
        self.__MapGrid = {}
        # ScaleBar信息
        self.__ScaleBar = {}
        # NorthArrow信息
        self.__NorthArrow = {}

        # tifFile
        self.__tifFile = ""
        # 专题图叠加其他图片信息
        self.__lyrMap = {}
        # 专题图叠加RGB三通道合成信息
        self.__rgbMap = {}
        # tif与矢量相交的点集合
        self.__staMap = ""
        # shpFile
        self.__shpFile = ""
        # 矢量等级
        self.__shpMark = ""
        # 输出目录
        self.__outDir = ""
        # 期次Labeltext
        self.__issueLabelText = ""

        # 分级，赋色，label信息
        self.__Colors = ""
        self.__ColorLevels = ""
        self.__ColorLabels = ""

    def AddLayoutInfotoMap(self, LayoutMap):
        """添加Layoout属性"""
        self.__printResolution = float(LayoutMap['printResolution'])
        self.__drivenPages = LayoutMap['drivenPages']
        self.__Margin = float(LayoutMap['Margin'])

    def AddPageSetupInfotoMap(self, PageCollectionMap):
        """添加PageSetup信息"""
        for key, value in PageCollectionMap.items():
            if key == "FrameColor" or key == "BackgroundColor":
                red = float(value['red']) / 255.
                green = float(value['green']) / 255.
                blue = float(value['blue']) / 255
                aplha = float(value['alpha']) / 255.
                value = (red, green, blue, aplha)
            self.__PageSetup[key] = value

    def AddTitleInfoMap(self, TitleMap):
        """添加title信息"""
        for key, value in TitleMap.items():
            if key == "FrameColor" or key == "BackgroundColor" or key == "FontColor":
                red = float(value['red']) / 255.
                green = float(value['green']) / 255.
                blue = float(value['blue']) / 255
                aplha = float(value['alpha']) / 255.
                value = (red, green, blue, aplha)
                value = (red, green, blue, aplha)
            if key == "LabelFont":
                value = value['description'].split(",")
                value[1] = float(value[1])
                value[2] = float(value[2])
                value = tuple(value)
            self.__Title[key] = value

    def AddAnnotationInfotoMap(self, AnnotationMap):
        """添加Annotation信息"""

        for num, annotations in AnnotationMap.items():

            self.__Annotation[num] = {}

            for key in annotations.keys():
                if key == "Font":
                    for fontkey, fontvalue in annotations[key].items():
                        if fontkey == "family":
                            key = "FontFamily"
                        elif fontkey == "Size":
                            key = "FontSize"
                        elif fontkey == "weight":
                            key = "FontWeight"
                        elif fontkey == "color":
                            key = "FontColor"
                        self.__Annotation[num][key] = fontvalue
                elif key == "Mark":
                    for markkey, markvalue in annotations[key].items():
                        if markkey == "marker":
                            key = "Marker"
                        elif markkey == "Color":
                            key = "MarkerColor"
                        elif markkey == "size":
                            key = "MarkerSize"
                        self.__Annotation[num][key] = markvalue
                else:
                    self.__Annotation[num][key] = annotations[key]

    def AddPictureInfotoMap(self, PictureMap):
        """添加Picture信息"""
        for num, pictures in PictureMap.items():

            self.__Picture[num] = {}

            for key, value in pictures.items():
                if key == "FrameColor" or key == "BackgroundColor":
                    red = float(value['red']) / 255.
                    green = float(value['green']) / 255.
                    blue = float(value['blue']) / 255
                    aplha = float(value['alpha']) / 255.
                    value = (red, green, blue, aplha)
                if key == "positionOnPage":
                    value = [float(x) for x in value.split(",")]
                self.__Picture[num][key] = value

    def AddLabelInfotoMap(self, LabelMap):
        """添加Label信息"""
        for num, labels in LabelMap.items():

            self.__Label[num] = {}

            for key, value in labels.items():
                if key == "FrameColor" or key == "BackgroundColor" or key == "FontColor":
                    red = float(value['red']) / 255.
                    green = float(value['green']) / 255.
                    blue = float(value['blue']) / 255
                    aplha = float(value['alpha']) / 255.
                    value = (red, green, blue, aplha)
                if key == 'LabelFont':
                    value = value['description'].split(",")
                    value[1] = float(value[1])
                    value[2] = float(value[2])
                    value = tuple(value)

                self.__Label[num][key] = value

    def AddIssueInfotoMap(self, IssueMap):
        """添加期次信息"""
        for key, value in IssueMap.items():
            if key == "FrameColor" or key == "BackgroundColor" or key == "FontColor":
                red = float(value['red']) / 255.
                green = float(value['green']) / 255.
                blue = float(value['blue']) / 255
                aplha = float(value['alpha']) / 255.
                value = (red, green, blue, aplha)
            if key == 'LabelFont':
                value = value['description'].split(",")
                value[1] = float(value[1])
                value[2] = float(value[2])
                value = tuple(value)
            self.__Issue[key] = value

    def AddAtlasInfotoMap(self, AtlasMap):
        """添加Atlas信息"""

        for num, atlas in AtlasMap.items():

            self.__Atlas[num] = {}

            for key, value in atlas.items():
                if key == "FrameColor" or key == "BackgroundColor":
                    red = float(value['red']) / 255.
                    green = float(value['green']) / 255.
                    blue = float(value['blue']) / 255
                    aplha = float(value['alpha']) / 255.
                    value = (red, green, blue, aplha)
                self.__Atlas[num][key] = value

    def AddDataFrameInfotoMap(self, DataFrameMap):
        """添加DataFrame信息"""

        for key, value in DataFrameMap.items():
            if key != "ComposerMapGrid":
                if key == "FrameColor" or key == "BackgroundColor":
                    value = [float(x) / 255 for x in value]
                elif key == "positionOnPage":
                    value = [float(x) for x in value.split(",")]

                self.__DataFrame[key] = value

    def AddMapGridInfotoMap(self, DataFrameMap):
        """添加MapGrid信息"""

        for key, value in DataFrameMap['ComposerMapGrid'].items():
            if key == "gridFrameStyle" or key == "gridFrameWidth" or key == "gridFramePenThickness" or \
                    key == "gridFramePad":
                value = float(value)
            elif key == "gridFramePenColor":
                value = [float(x) for x in value.split(",")]
            elif key == "annotationFontProperties":
                font = value['description'].split(",")[0]
                size = value['description'].split(",")[1]
                value = (font, float(size))
            self.__MapGrid[key] = value

    def AddScaleBarInfotoMap(self, ScaleBarMap):
        """添加ScaleBar信息"""
        for num, scalebars in ScaleBarMap.items():
            self.__ScaleBar[num] = {}

            for key, value in scalebars.items():
                if key == 'fillColor' or key == 'fillColor2':
                    red = float(value['red']) / 255.
                    green = float(value['green']) / 255.
                    blue = float(value['blue']) / 255
                    aplha = float(value['alpha']) / 255.
                    value = (red, green, blue, aplha)
                    self.__ScaleBar[num][key] = value

                elif key == 'text-style':
                    for subkey in value.keys():
                        self.__ScaleBar[num][subkey] = value[subkey]

                else:
                    self.__ScaleBar[num][key] = value

    def AddNorthArrowInfotoMap(self, NorthArrowMap):
        """添加NorthArrow信息"""
        for num, NorthArrows in NorthArrowMap.items():

            self.__NorthArrow[num] = {}

            for key, value in NorthArrows.items():
                if key == 'Font':
                    for subkey in value.keys():
                        self.__NorthArrow[num][subkey] = value[subkey]
                else:
                    self.__NorthArrow[num][key] = value

    def AddtifFiletoMap(self, tifFile):
        """添加tif文件"""
        if os.path.exists(tifFile):
            self.__tifFile = tifFile
        else:
            return

    def AddlyrOverlytoMap(self, lyr, RastersMap):
        """叠加栅格文件"""
        for num, Rasters in RastersMap.items():

            self.__lyrMap[num] = {}

            coverageLayerName = Rasters['coverageLayerName']
            Rev = Rasters['ReMaps']['Rev']
            Color = Rasters['ReMaps']['Color']
            Label = Rasters['ReMaps']['Label']
            zorder = int(Rasters['zorder'])

            # 判断是否为外部依赖
            isOutRaster = Rasters['isOutRaster']
            if isOutRaster == "true" or isOutRaster == "True":
                file = Rasters['file']
                self.__lyrMap[num]['file'] = file
                self.__lyrMap[num]['coverageLayerName'] = coverageLayerName
                self.__lyrMap[num]['Rev'] = Rev
                self.__lyrMap[num]['Color'] = Color
                self.__lyrMap[num]['Label'] = Label
                self.__lyrMap[num]['zorder'] = zorder
            elif isOutRaster == "false" or isOutRaster == "False":
                for lyrName, lyrPath in lyr.items():
                    if lyrName == coverageLayerName:
                        self.__lyrMap[num]['file'] = lyrPath
                        self.__lyrMap[num]['coverageLayerName'] = coverageLayerName
                        self.__lyrMap[num]['Rev'] = Rev
                        self.__lyrMap[num]['Color'] = Color
                        self.__lyrMap[num]['Label'] = Label
                        self.__lyrMap[num]['zorder'] = zorder

    def AddRGBFileMaptoMap(self, rgbPseudo, RGBFileMap):
        """RGB三通道合成文件"""
        for num, RGBFile in RGBFileMap.items():

            isOutRaster = RGBFile['isOutRaster']
            coverageLayerName = RGBFile['coverageLayerName']
            zorder = int(RGBFile['zorder'])

            if isOutRaster == "true" or isOutRaster == "True":
                file = RGBFile['file']
                self.__rgbMap['file'] = file
                self.__rgbMap['coverageLayerName'] = coverageLayerName
                self.__rgbMap['zorder'] = zorder
            elif isOutRaster == "false" or isOutRaster == "False":
                for rgbName, rgbPath in rgbPseudo.items():
                    if rgbName == coverageLayerName:
                        self.__rgbMap['file'] = rgbPath
                        self.__rgbMap['coverageLayerName'] = coverageLayerName
                        self.__rgbMap['zorder'] = zorder

    def AddstaMaptoMap(self, staMap):
        self.__staMap = staMap

    def AddshpFiletoMap(self, shpFile):
        """添加shp文件"""
        if os.path.exists(shpFile):
            self.__shpFile = shpFile
        else:
            return

    def AddshpMarktoMap(self, shpMark):
        """添加矢量等级"""
        self.__shpMark = shpMark

    def AddoutDirtoMap(self, outDir):
        """添加输出目录"""
        self.__outDir = outDir

    def AddissueLabelTexttoMap(self, issueLabelText):
        """监测时间"""
        self.__issueLabelText = issueLabelText

    def AddColorstoMap(self, Colors):
        self.__Colors = Colors

    def AddColorLevelstoMap(self, ColorLevels):
        self.__ColorLevels = ColorLevels

    def AddColorLabelstoMap(self, ColorLabels):
        self.__ColorLabels = ColorLabels

    def getPlugainName(self):
        return self.__plugainName

    def gettifFile(self):
        return self.__tifFile

    def getlyrMap(self):
        return self.__lyrMap

    def getrgbPseudoMap(self):
        return self.__rgbMap

    def getstaMap(self):
        return self.__staMap

    def getshpFile(self):
        return self.__shpFile

    def getshpMark(self):
        return self.__shpMark

    def getoutDir(self):
        return self.__outDir

    def getissueLabelText(self):
        return self.__issueLabelText

    def getprintResolution(self):
        return self.__printResolution

    def getdrivenPages(self):
        flag = bool

        if self.__drivenPages == 'True' or self.__drivenPages == "true":
            flag = True
        elif self.__drivenPages == 'False' or self.__drivenPages == "false":
            flag = False

        return flag

    def getMargin(self):
        return self.__Margin

    def getPageSetup(self):
        return self.__PageSetup

    def getDataFrame(self):
        return self.__DataFrame

    def getMapGrid(self):
        return self.__MapGrid

    def getTitle(self):
        return self.__Title

    def getLabel(self):
        return self.__Label

    def getIssue(self):
        return self.__Issue

    def getPicture(self):
        return self.__Picture

    def getAtlas(self):
        return self.__Atlas

    def getAnnotation(self):
        return self.__Annotation

    def getScalBar(self):
        return self.__ScaleBar

    def getNorthArrow(self):
        return self.__NorthArrow

    def getColors(self):
        return self.__Colors

    def getColorLevels(self):
        return self.__ColorLevels

    def getColorLabels(self):
        return self.__ColorLabels
