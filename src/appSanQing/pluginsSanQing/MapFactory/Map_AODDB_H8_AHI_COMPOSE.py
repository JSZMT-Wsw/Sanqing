# -*- coding: utf-8 -*-
'''
@File  : Map_AODDB_H8_AHI_COMPOSE.py
@Author: admin#
@Date  : 2020/11/19 13:39
@Desc  : 
'''
import numpy as np
from src.common.CartopyMapPy.Layout.Process.BaseProcess import BaseProcess
import os
import matplotlib.pyplot as plt
import shapefile
from pylab import mpl
from PIL import Image
from tqdm import tqdm
from src.common.CartopyMapPy.Layout.tools.OsgeoTools import OsgeoTools
from src.common.utils.FileUtil import BaseFile
from shapely.geometry import Polygon, Point
from src.common.CartopyMapPy.Layout.tools.ColorTrans import ColorTrans

mpl.rcParams['font.sans-serif'] = 'FangSong'  # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题


class Map_AODDB_H8_AHI_COMPOSE(BaseProcess):
    """AOD_H8_AHI绘图"""

    def __init__(self, mapInfo):
        BaseProcess.__init__(self, mapInfo)

    def DrivenPageMap(self):
        """DrivenPage专题图"""
        try:
            sf = shapefile.Reader(self.shpFile)  # encoding参数读取中文 , encoding='gb18030'
            borders = sf.shapes()  # 几何信息
            desc = os.path.basename(self.shpFile).replace("\\", '/')
            pbar = tqdm(range(len(borders)))
            for i in pbar:
                pbar.set_description(desc=desc, refresh=i)
                border = sf.shape(i)  # 第i个shape类的点集信息
                # x, y = zip(*border.points)

                # 01 获取当前feature下的属性表信息
                id = sf.record(i).ID  # 第i个shape类属性表中ID字段的信息
                name = sf.record(i).NAME  # 第i个shape类属性表中NAME字段的信息
                if id not in self.staMap.keys():  # tif与当前行政区划无交集
                    continue

                bbox = border.bbox  # 第i个shape类的 左下角 Lon,Lat  +   右上角 Lon,Lat
                # 02 数据获取并插值处理
                data, geotrans = OsgeoTools.readTifByShp(self.tifFile, self.shpFile, "ID", id, 2)

                # 03  重新计算ShpExtent, MapExtent, figsize
                self.DataFrame, self.PageSetup = OsgeoTools.CalPageLayout(bbox, self.Margin, self.mapW,
                                                                          self.printResolution, self.DataFrame,
                                                                          self.PageSetup)

                # 04 绘图
                fig = self.PlotComp(id, name, border, bbox, data, geotrans)
                # 保存
                if BaseFile.isFileOrDir(os.path.join(self.outDir, id)) != BaseFile.ISDIR:
                    BaseFile.creatDir(os.path.join(self.outDir, id))
                regionPath = os.path.join(self.outDir, id + "/" + id + ".png")
                temp_fig = regionPath.replace(".png", "_temp.png")
                fig.savefig(temp_fig, dpi=fig.dpi)
                im = Image.open(temp_fig)
                (x, y) = im.size
                out = im.resize((int(0.7*x), int(0.7*y)), Image.ANTIALIAS)
                out.save(regionPath)
                os.remove(temp_fig)
                plt.close()


                # 返回文件列表
                if BaseFile.isFileOrDir(regionPath) == BaseFile.ISFILE:
                    self.returnJPGMap[id] = regionPath

            return True
        except Exception as e:
            print(e)
            return False

    def PlotComp(self, id, name, border, bbox, data, geotrans):
        """绘制专题图"""
        # 添加画布
        fig = self.AddPage(self.PageSetup, self.printResolution)
        # 添加绘图区
        ax = self.AddMap(fig, self.DataFrame, self.MapGrid, self.shpMark)
        # 添加系统内置feature
        self.AddSysFeature(ax)
        # 添加标题
        self.AddTitle(fig, self.Title, name)
        # 添加期次
        self.AddIssue(fig, self.Issue, self.issueLabelText)
        # 添加Label
        self.AddLabel(fig, self.Label)
        # 添加矢量
        self.AddAtlas(ax, self.Atlas)
        # 添加城市标注
        self.AddAnnotation(ax, self.Annotation, border.points)
        # 添加指北针
        self.AddNorthArrow(ax, self.NorthArrow)
        # 添加比例尺
        self.AddScalBar(fig, self.ScaleBar)
        # 颜色渐进
        self.getColors(data, self.colors, self.colorlevels)
        # tif渲染
        self.ClassifiedImshow(ax, data, geotrans, self.colorlevelsDrow, self.colorsDrow)
        # 添加ColorBar
        self.AddColorBar(fig, ax, data, self.colorlevels, self.colors, self.colorlabels)
        # lyrMap叠加渲染
        self.lyrMapImshow(fig, ax, self.lyrMap, id, bbox)
        # 添加南海子图
        self.AddSouthChinaSea(fig, ax, self.DataFrame['Extent'])

        return fig
    def AddIssue(self, fig, Issue, issueLabelText):
        """添加期次"""
        try:
            rect = Issue['positionOnPage'].split(",")
            rect = [float(x) for x in rect]
            axIssue = fig.add_axes(rect,
                                   frameon=Issue['frame'],  # 是否显示标签框
                                   facecolor=Issue['BackgroundColor'])  # 标签框的填充色

            axIssue.get_yaxis().set_visible(False)  # 不显示y轴刻度
            axIssue.get_xaxis().set_visible(False)  # 不显示x轴刻度

            # ax.axison = False # ax的显隐设置

            for side in ['left', 'right', 'bottom', 'top']:  # 标签框的线条设置
                axIssue.spines[side].set_color(Issue['FrameColor'])  # 线条颜色
                axIssue.spines[side].set_linewidth(float(Issue['outlineWidthM']))  # 线条粗细
                axIssue.spines[side].set_linestyle('--')  # 线条样式

            # 标签字体设置
            fontdict = {'family': Issue['LabelFont'][0],  # 字体样式
                        'size': Issue['LabelFont'][1],  # 字体大小
                        'weight': Issue['LabelFont'][2],  # 字体宽度
                        'color': Issue['FontColor']  # 字体颜色
                        }

            tempText = None
            # labelText设置
            if "年" in Issue['labelText']:
                tempText = issueLabelText[0:4] + "年"
            if "月" in Issue['labelText'] and int(issueLabelText[4:6]) != 0:
                tempText += str(int(issueLabelText[4:6])) + "月"
            if "日" in Issue['labelText'] and int(issueLabelText[6:8]) != 0:
                tempText += str(int(issueLabelText[6:8])) + "日"
            if "时" in Issue['labelText']:
                tempText += str(int(issueLabelText[8:10])) + "时"
            if "分" in Issue['labelText']:
                tempText += issueLabelText[10:12] + "分"
            Issue['labelText'] = tempText

            # Issue['labelText'] = issueLabelText[0:4] + "年" + issueLabelText[4:6] + "月" + issueLabelText[6:8] + "日"
            axIssue.text(0.5, 0.5, Issue['labelText'],
                         fontdict=fontdict,
                         horizontalalignment='center',
                         verticalalignment='center',
                         # transform=axText.transAxes
                         )
        except Exception as e:
            print(e)
            print("期次添加失败")
            return
    def AddAnnotation(self, ax, Annotation, pointsList):
        """
        添加城市标注
        第i个shape类的 左下角 Lon,Lat  +   右上角 Lon,Lat
        """
        try:
            poly = Polygon(pointsList)
            for num, property in Annotation.items():
                lon, lat = float(property['lon']), float(property['lat'])

                point = Point(lon, lat)
                flag = point.within(poly)
                # if not (flag):
                #     continue

                color = property['MarkerColor'].split(",")
                color = [float(x) / 255.0 for x in color]

                FontColor = property['FontColor'].split(",")
                FontColor = [float(x) / 255.0 for x in FontColor]
                fontdict = {'family': property['FontFamily'],  # 字体样式
                            'size': float(property['FontSize']),  # 字体大小
                            'weight': float(property['FontWeight']),  # 字体宽度
                            'color': FontColor  # 字体颜色
                            }

                ax.text(lon, lat, property['name'], fontdict=fontdict, zorder=98)
        except Exception as e:
            print(e)
            print("城市标注添加出错")
            return False
