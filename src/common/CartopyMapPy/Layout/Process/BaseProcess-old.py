# encoding: utf-8
"""
@author: DYX
@file: BaseProcess.py
@time: 2020/10/20 13:56
@desc:
"""
import os
import time

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors as mcolors
import matplotlib.image as mpimg
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import shapefile
from shapely.geometry import Polygon, Point
from cartopy.io.shapereader import Reader
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from pylab import mpl
from tqdm import tqdm

from src.common.CartopyMapPy.Layout.tools.ColorTrans import ColorTrans
from src.common.CartopyMapPy.Layout.tools.OsgeoTools import OsgeoTools
from src.common.utils.FileUtil import BaseFile

mpl.rcParams['font.sans-serif'] = 'SimHei'  # 指定默认字体  Times New Roman
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

"""
注：
在代码中关于zorder的问题，有些是在代码中给定
``指北针		zorder=100
``经纬格网	zorder=99
``城市注记	zorder=98
``Picture	zorder=97
``Contourf	zorder=5
``比例尺		zorder=95
"""


class BaseProcess:
    """出图函数基类"""

    def __init__(self, mapInfo):
        LayoutDir = os.path.dirname(os.path.dirname(__file__))
        self.borderPath = os.path.dirname(LayoutDir) + "/depend/Sysborder/CN-border-La.dat"
        self.borders = None  # 系统内置边界

        # self.Margin = 107  # map缩放比
        self.mapW = 10  # 中间地图大小 一般给定10
        self.transparent = True

        self.returnJPGMap = {}  # 输出文件
        self.returnPNGMap = {}  # 输出文件

        # 栅格数据信息
        self.data = None
        self.geotrans = None
        self.minV = None
        self.maxV = None

        # Legend信息
        self.colorlevels = mapInfo.getColorLevels()  # 分级刻度  包含两端点
        self.colors = mapInfo.getColors()  # 分级区间颜色
        self.colorlabels = mapInfo.getColorLabels()  # 分级区间标签

        # 文件夹/文件获取
        self.tifFile = mapInfo.gettifFile()
        self.staMap = mapInfo.getstaMap()
        self.shpFile = mapInfo.getshpFile()
        self.shpMark = mapInfo.getshpMark()
        self.outDir = mapInfo.getoutDir()
        self.issueLabelText = mapInfo.getissueLabelText()

        self.printResolution = mapInfo.getprintResolution()  # dpi
        self.drivenPages = mapInfo.getdrivenPages()  # 驱动
        self.Margin = mapInfo.getMargin()  # map缩放比

        self.DataFrame = mapInfo.getDataFrame()
        self.MapGrid = mapInfo.getMapGrid()
        self.PageSetup = mapInfo.getPageSetup()
        self.Title = mapInfo.getTitle()
        self.Label = mapInfo.getLabel()
        self.Issue = mapInfo.getIssue()
        self.Picture = mapInfo.getPicture()
        self.Atlas = mapInfo.getAtlas()
        self.Annotation = mapInfo.getAnnotation()
        self.ScaleBar = mapInfo.getScalBar()
        self.NorthArrow = mapInfo.getNorthArrow()

        self.doInit()

    def doInit(self):
        """参数初始计算"""
        with open(self.borderPath) as src:
            context = src.read()

        blocks = [cnt for cnt in context.split(">") if len(cnt) > 0]
        self.borders = [np.fromstring(block, dtype=float, sep=" ") for block in blocks]

        # MapExtent 计算
        # 注: 2020/11/18改动，该内容在这里不合适 该方法适用于no drivenPages。
        # ShpExtent, MapExtent = OsgeoTools.CalMapExtent(self.shpFile, self.Margin)
        # self.DataFrame['Extent']['xmin'] = MapExtent[0]
        # self.DataFrame['Extent']['xmax'] = MapExtent[1]
        # self.DataFrame['Extent']['ymin'] = MapExtent[2]
        # self.DataFrame['Extent']['ymax'] = MapExtent[3]
        # self.DataFrame['ShpExtent'] = {'xmin': ShpExtent[0],
        #                                'xmax': ShpExtent[1],
        #                                'ymin': ShpExtent[2],
        #                                'ymax': ShpExtent[3]}

        # figsize计算
        # 注: 2020/11/18改动，该内容在这里不合适 该方法适用于no drivenPages。
        # ratio = (MapExtent[1] - MapExtent[0]) / (MapExtent[3] - MapExtent[2])
        # mapPosition = self.DataFrame['positionOnPage']
        #
        # mapW = self.mapW
        # mapH = mapW / ratio
        #
        # figW = mapW / mapPosition[2] * self.printResolution / 100.
        # figH = mapH / mapPosition[3] * self.printResolution / 100.
        # self.PageSetup['size'] = (figW, figH)

        # tif数据读取
        data, XSize, YSize, geotrans, proj, (minV, maxV) = OsgeoTools.read_tiff(self.tifFile, 1)
        self.data = data
        self.geotrans = geotrans
        self.minV = minV
        self.maxV = maxV

        # 颜色RGB转16进制
        self.colors = [ColorTrans.RGB_to_Hex(x) for x in self.colors]

    def doMap(self):
        # 设置fig属性

        if self.drivenPages:
            flag = self.DrivenPageMap()
            if flag:
                return True
            else:
                return False

    def AddPage(self, PageSetup, printResolution):
        """
        页面绘制

        plt.figure参数意义:
        figsize : (float, float)
            Width, height 画布页面大小
        dpi : float
        facecolor : [R, G, B]/[R, G, B, A]  数值大小float
            画布填充色
        edgecolor : [R, G, B]/[R, G, B, A]  数值大小float
            画布框图边缘线颜色
        frameon : bool
            控制填充色和边缘线是否显示 frameon=False，则facecolor和edgecolor设置无效
        linewidth : float
            边缘线宽度
        """
        try:
            fig = plt.figure(figsize=PageSetup['size'],
                             dpi=printResolution,
                             facecolor=PageSetup['BackgroundColor'],
                             edgecolor=PageSetup['FrameColor'],
                             frameon=PageSetup['frame'],
                             linewidth=PageSetup['outlineWidthM']
                             )

            return fig
        except:
            print("画布设置错误")
            return

    def AddMap(self, fig, DataFrame, MapGrid, shpMark):
        """
        添加绘图区

        rect : [left, bottom, width, height]    绘图区相对位置
        frameon : bool  会图框是否显示
        facecolor : 控制填充色和边缘线是否显示 frameon=False，则facecolor和edgecolor设置无效
        projection : 地图投影信息

        """
        try:
            rect = DataFrame['positionOnPage']
            ax = fig.add_axes(rect,
                              frameon=DataFrame['frame'],
                              facecolor=DataFrame['BackgroundColor'],
                              projection=ccrs.PlateCarree(),
                              )

            # [minLon, maxLon, minLat, maxLat]
            extent = [DataFrame['Extent']['xmin'],
                      DataFrame['Extent']['xmax'],
                      DataFrame['Extent']['ymin'],
                      DataFrame['Extent']['ymax']]
            ax.set_extent(extent, crs=ccrs.PlateCarree())

            # 去除绘图区轴刻度方法一
            # plt.gca().xaxis.set_major_locator(plt.NullLocator())
            # plt.gca().yaxis.set_major_locator(plt.NullLocator())

            # 去除绘图区轴刻度方法二
            # ax.get_yaxis().set_visible(False)  # 不显示y轴
            # ax.get_xaxis().set_visible(False)  # 不显示x轴

            # 不显示刻度
            # ax.set_xticks([])
            # ax.set_yticks([])

            # ax的显隐设置
            ax.axison = True

            # 绘图框边缘线设置  注:ax.spines['left'].set_color() 不起作用，只能用geo关键字
            # python2上用ax.spines['left'].set_color()
            # python3上用ax.spines['geo']
            # for spine in ['left', 'right', 'bottom', 'top']:
            # 	ax.spines[spine].set_color(DataFrame['FrameColor'])
            # 	ax.spines[spine].set_linewidth(DataFrame['outlineWidthM'])
            # 	ax.spines[spine].set_linestyle('--')

            ax.spines['geo'].set_color(DataFrame['FrameColor'])
            ax.spines['geo'].set_linewidth(DataFrame['outlineWidthM'])
            ax.spines['geo'].set_linestyle('-')

            # 添加经纬网
            ax = self.ModifyGrid(ax, DataFrame, MapGrid, shpMark)  # 注：在添加经纬网之后，此时的rect已经变了，因为有经纬度标注

            if not (ax) is None:
                return ax
            else:
                return ax
        except:
            print("绘图区设置错误")
            return

    def ModifyGrid(self, ax, DataFrame, MapGrid, shpMark):
        """
        经纬网绘制及标注
        https://blog.csdn.net/helunqu2017/article/details/78736554
        1. gridlines
            linestyle : 经纬网样式
            lw : 经纬网线条宽度
            color : 经纬网线条颜色
        2. tick_params
            labelsize : 标注字体大小
            pad : 标注与框图间隔
        3. set_fontname 标注字体样式

        4. set_major_formatter : 标注字体添加E，N

        """
        try:
            minLon = DataFrame['Extent']['xmin']
            maxLon = DataFrame['Extent']['xmax']
            minLat = DataFrame['Extent']['ymin']
            maxLat = DataFrame['Extent']['ymax']

            level = ""
            if shpMark == "County":
                level = 4
            elif shpMark == "City":
                level = 2
            elif shpMark == "Province":
                level = 1
            elif shpMark == "Nation":
                level = 1

            gab = float(MapGrid['gridFrameWidth']) / level

            xticks = list(np.arange(round(minLon - 1.1), round(maxLon + 1.1), gab))
            xticks = [x for x in xticks if minLon <= x <= maxLon]
            yticks = list(np.arange(round(minLat - 1.1), round(maxLat + 1.1), gab))
            yticks = [y for y in yticks if minLat <= y <= maxLat]

            # 绘制经纬网格
            color = [x / 255 for x in MapGrid['gridFramePenColor']]
            ax.gridlines(xlocs=xticks, ylocs=yticks,
                         linestyle='--',
                         lw=MapGrid['gridFramePenThickness'],
                         color=color,
                         zorder=99)

            # 添加标注
            ax.set_xticks(xticks, crs=ccrs.PlateCarree())
            ax.set_yticks(yticks, crs=ccrs.PlateCarree())

            labelsize = MapGrid['annotationFontProperties'][1]  # 标注字体大小
            pad = MapGrid['gridFramePad']  # 标注与框图间隔
            ax.tick_params(labelsize=labelsize,
                           pad=pad)

            fonname = MapGrid['annotationFontProperties'][0]  # 标注字体样式
            labels = ax.get_xticklabels() + ax.get_yticklabels()
            [label.set_fontname(fonname) for label in labels]

            lon_formatter = LongitudeFormatter(zero_direction_label=False)  # zero_direction_label用来设置经度的0度加不加E和W
            lat_formatter = LatitudeFormatter()
            ax.xaxis.set_major_formatter(lon_formatter)  # 给定N, E样式
            ax.yaxis.set_major_formatter(lat_formatter)

            return ax
        except:
            print('修改经纬网格出错')
            return

    def AddTitle(self, fig, Title, name):
        """
        添加标题
        set_title方法设置的title位置不固定
        label = name + Title['labelText']
        fontdict = {'fontsize': Title['LabelFont'][1],
                    'fontweight': Title['LabelFont'][2],
                    'color': Title['FontColor'],
                    'family': Title['LabelFont'][0],
                    'verticalalignment': 'baseline',
                    'horizontalalignment': 'center'}
        pad = float(Title['pad'])
        y = float(Title['y'])
        ax.set_title(label, fontdict=fontdict, pad=pad, y=y)

        """
        try:
            if Title.keys() == None:
                return

            rect = Title['positionOnPage'].split(",")
            rect = [float(x) for x in rect]
            axText = fig.add_axes(rect,
                                  frameon=Title['frame'],  # 是否显示标签框
                                  facecolor=Title['BackgroundColor'])  # 标签框的填充色

            axText.get_yaxis().set_visible(False)  # 不显示y轴刻度
            axText.get_xaxis().set_visible(False)  # 不显示x轴刻度

            # ax.axison = False # ax的显隐设置

            for side in ['left', 'right', 'bottom', 'top']:  # 标签框的线条设置
                axText.spines[side].set_color(Title['FrameColor'])  # 线条颜色
                axText.spines[side].set_linewidth(float(Title['outlineWidthM']))  # 线条粗细
                axText.spines[side].set_linestyle('--')  # 线条样式

            # 标签字体设置
            fontdict = {'family': Title['LabelFont'][0],  # 字体样式
                        'fontsize': Title['LabelFont'][1],  # 字体大小
                        'fontweight': Title['LabelFont'][2],  # 字体宽度
                        'color': Title['FontColor']  # 字体颜色
                        }

            label = (name + Title['labelText'])
            axText.text(0.5, 0.5, label,
                        fontdict=fontdict,
                        horizontalalignment='center',
                        verticalalignment='center',
                        # transform=axText.transAxes
                        )

            return True
        except:
            return False

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
            if "月" in Issue['labelText']:
                tempText += str(int(issueLabelText[4:6])) + "月"
            if "日" in Issue['labelText']:
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
            return True
        except:
            print("期次添加失败")
            return False

    def AddLabel(self, fig, Label):
        """添加标签"""
        try:
            for num, attribute in Label.items():

                # 标签框设置
                rect = attribute['positionOnPage'].split(",")
                rect = [float(x) for x in rect]
                axText = fig.add_axes(rect,
                                      frameon=attribute['frame'],  # 是否显示标签框
                                      facecolor=attribute['BackgroundColor'])  # 标签框的填充色

                axText.get_yaxis().set_visible(False)  # 不显示y轴刻度
                axText.get_xaxis().set_visible(False)  # 不显示x轴刻度

                # ax.axison = False # ax的显隐设置

                for side in ['left', 'right', 'bottom', 'top']:  # 标签框的线条设置
                    axText.spines[side].set_color(attribute['FrameColor'])  # 线条颜色
                    axText.spines[side].set_linewidth(float(attribute['outlineWidthM']))  # 线条粗细
                    axText.spines[side].set_linestyle('--')  # 线条样式

                # 标签字体设置
                fontdict = {'family': attribute['LabelFont'][0],  # 字体样式
                            'size': attribute['LabelFont'][1],  # 字体大小
                            'weight': attribute['LabelFont'][2],  # 字体宽度
                            'color': attribute['FontColor']  # 字体颜色
                            }
                axText.text(0.5, 0.5, attribute['labelText'],
                            fontdict=fontdict,
                            horizontalalignment='center',
                            verticalalignment='center',
                            # transform=axText.transAxes
                            )
            return True
        except:
            print('标签添加失败')
            return

    def AddPicture(self, fig, Picture):
        """添加图片 控制宽度百分比即可"""

        try:
            for num, attribute in Picture.items():

                # 图片相对长、宽
                img = mpimg.imread(attribute['file'])
                imgW = img.shape[1] / 1000.0
                imgH = img.shape[0] / 1000.0
                ratio = imgW / imgH

                # 图片位置重置
                width = attribute['positionOnPage'][2]
                height = width / ratio
                attribute['positionOnPage'][3] = height

                imgRW = int(width * 1000)
                imgRH = int(height * 1000)

                rect = attribute['positionOnPage']
                axPic = fig.add_axes(rect,
                                     frameon=attribute['frame'],  # 是否显示标签框
                                     facecolor=attribute['BackgroundColor'])  # 标签框的填充色

                axPic.get_yaxis().set_visible(False)  # 不显示y轴刻度
                axPic.get_xaxis().set_visible(False)  # 不显示x轴刻度
                for side in ['left', 'right', 'bottom', 'top']:  # 标签框的线条设置
                    axPic.spines[side].set_color(attribute['FrameColor'])  # 线条颜色
                    axPic.spines[side].set_linewidth(attribute['outlineWidthM'])  # 线条粗细
                    axPic.spines[side].set_linestyle('--')  # 线条样式

                axPic.imshow(img, extent=[0, imgRW, 0, imgRH], zorder=97)  # imshow()绘图，会有0.5个像素的偏差

            return True
        except:
            print("添加图片失败")
            return False

    def AddAtlas(self, ax, Altas):
        """添加矢量"""

        try:
            for num, layerPropertys in Altas.items():
                filename = layerPropertys['file']
                reader = Reader(filename)

                feature = cfeature.ShapelyFeature(reader.geometries(), ccrs.PlateCarree(),
                                                  facecolor=layerPropertys['BackgroundColor'],
                                                  edgecolor=layerPropertys['FrameColor'])
                linewidth = float(layerPropertys['outlineWidthM'])
                zorder = int(layerPropertys['zorder'])
                ax.add_feature(feature, linewidth=linewidth, linestyle=layerPropertys['linestyle'], zorder=zorder)
            return True
        except:
            print("添加矢量失败")
            return False

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
                if not (flag):
                    continue

                marker = property['Marker']
                s = float(property['MarkerSize'])
                color = property['MarkerColor'].split(",")
                color = [float(x) / 255.0 for x in color]

                FontColor = property['FontColor'].split(",")
                FontColor = [float(x) / 255.0 for x in FontColor]
                fontdict = {'family': property['FontFamily'],  # 字体样式
                            'size': float(property['FontSize']),  # 字体大小
                            'weight': float(property['FontWeight']),  # 字体宽度
                            'color': FontColor  # 字体颜色
                            }

                ax.scatter(lon, lat, marker=marker, s=s, color=color, zorder=98)
                ax.text(lon - 0.15, lat + 0.05, property['name'], fontdict=fontdict, zorder=98)
            return True
        except:
            print("城市标注添加出错")
            return False

    def AddNorthArrow(self, ax, NorthArrow):
        """
        绘制指北针
        loc_x : 指北针符号中间列位置
        loc_y : N字体底部高度
        width : 指北针符号宽度
        height : 指北针符号高度
        pad : 指北针符号底部-->N字体底部高度
        """
        try:
            for num, property in NorthArrow.items():
                loc_x = float(property['positionOnPage'].split(",")[0])
                loc_y = float(property['positionOnPage'].split(",")[1])
                width = float(property['Width'])
                height = float(property['Height'])
                pad = float(property['pad'])

                minx, maxx = ax.get_xlim()
                miny, maxy = ax.get_ylim()
                ylen = maxy - miny
                xlen = maxx - minx

                left = [minx + xlen * (loc_x - width * .5), miny + ylen * (loc_y - pad)]
                right = [minx + xlen * (loc_x + width * .5), miny + ylen * (loc_y - pad)]
                top = [minx + xlen * loc_x, miny + ylen * (loc_y - pad + height)]
                center = [minx + xlen * loc_x, left[1] + (top[1] - left[1]) * .4]
                triangle1 = mpatches.Polygon([left, top, center], facecolor='k', edgecolor='k', zorder=100)
                triangle2 = mpatches.Polygon([right, top, center], facecolor='w', edgecolor='k', zorder=100)

                ax.add_patch(triangle1)
                ax.add_patch(triangle2)

                fontdict = {'family': property['fontFamily'],  # 字体样式
                            'size': property['fontSize'],  # 字体大小
                            'weight': property['fontWeight'],  # 字体宽度
                            }

                ax.text(s='N',
                        x=minx + xlen * loc_x,
                        y=miny + ylen * loc_y,
                        fontdict=fontdict,
                        horizontalalignment='center',
                        verticalalignment='bottom',
                        zorder=100)
            return True
        except:
            print('指北针绘制失败')
            return False

    def AddScalBar(self, fig, ScaleBar):
        """
        绘制比例尺
        projection=ccrs.PlateCarree()  添加该参数后，pos位置是错误的
        """
        try:
            L = 40075700  # 赤道周长 单位m

            MapExtent = self.DataFrame['Extent']  # 中间地图经纬度
            xlen = MapExtent['xmax'] - MapExtent['xmin']
            ylen = MapExtent['ymax'] - MapExtent['ymin']

            # 1km所代表的实际像素个数 (中间地图宽度像素数 / 中间地图宽度跨度实际距离km)
            trueWidth = L / 360 * xlen / 1000  # 中间地图实际宽度  单位km
            pixnum = float(self.mapW) * 100 / trueWidth

            # 画布像素数
            figsize = self.PageSetup['size']
            figWidthDPI = figsize[0] * int(self.printResolution)

            for num, property in ScaleBar.items():
                maxBarWidth = float(property['maxBarWidth'])  # 百分比长度
                minBarWidth = maxBarWidth / 16
                graduat = figWidthDPI * minBarWidth / pixnum

                rat = graduat - int(graduat)
                if rat < 0.4:
                    graduat = int(graduat)
                elif 0.4 <= rat <= 0.7:
                    graduat = int(graduat) + 0.5
                elif rat > 0.7:
                    graduat = int(graduat) + 1

                loc_x = float(property['positionOnPage'].split(",")[0])
                loc_y = float(property['positionOnPage'].split(",")[1])
                BarHeight = float(property['BarHeight'])

                # 绘制7个黑白相间矩形
                pos1 = [loc_x, loc_y, minBarWidth, BarHeight]
                pos2 = [loc_x + pos1[2], loc_y, minBarWidth, BarHeight]
                pos3 = [pos2[0] + pos2[2], loc_y, minBarWidth, BarHeight]
                pos4 = [pos3[0] + pos3[2], loc_y, minBarWidth, BarHeight]

                pos5 = [pos4[0] + pos4[2], loc_y, minBarWidth * 4, BarHeight]
                pos6 = [pos5[0] + pos5[2], loc_y, minBarWidth * 4, BarHeight]
                pos7 = [pos6[0] + pos6[2], loc_y, minBarWidth * 4, BarHeight]

                pos17 = [pos1[0], loc_y, minBarWidth * 16, BarHeight]

                sub_ax17 = fig.add_axes(pos17, frameon=True, facecolor='w')
                sub_ax17.set_xticks(
                    np.array([0, graduat * 2, graduat * 4, graduat * 8, graduat * 12, graduat * 16]))  # x周刻度
                [x.set_fontname(property['fontFamily']) for x in sub_ax17.get_xticklabels()]  # 字体样式调整
                sub_ax17.get_yaxis().set_visible(False)  # 不显示y轴
                sub_ax17.tick_params(length=0, zorder=95)  # 刻度线为0

                sub_ax1 = fig.add_axes(pos1, frameon=True, facecolor=property['fillColor'])
                sub_ax1.get_yaxis().set_visible(False)  # 不显示y轴
                sub_ax1.get_xaxis().set_visible(False)  # 不显示x轴
                sub_ax2 = fig.add_axes(pos2, frameon=True, facecolor=property['fillColor2'])
                sub_ax2.get_yaxis().set_visible(False)  # 不显示y轴
                sub_ax2.get_xaxis().set_visible(False)  # 不显示x轴
                sub_ax3 = fig.add_axes(pos3, frameon=True, facecolor=property['fillColor'])
                sub_ax3.get_yaxis().set_visible(False)  # 不显示y轴
                sub_ax3.get_xaxis().set_visible(False)  # 不显示x轴
                sub_ax4 = fig.add_axes(pos4, frameon=True, facecolor=property['fillColor2'])
                sub_ax4.get_yaxis().set_visible(False)  # 不显示y轴
                sub_ax4.get_xaxis().set_visible(False)  # 不显示x轴

                sub_ax5 = fig.add_axes(pos5, frameon=True, facecolor=property['fillColor'])
                sub_ax5.get_yaxis().set_visible(False)  # 不显示y轴
                sub_ax5.get_xaxis().set_visible(False)  # 不显示x轴

                sub_ax6 = fig.add_axes(pos6, frameon=True, facecolor=property['fillColor2'])
                sub_ax6.get_yaxis().set_visible(False)  # 不显示y轴
                sub_ax6.get_xaxis().set_visible(False)  # 不显示x轴

                sub_ax7 = fig.add_axes(pos7, frameon=True, facecolor=property['fillColor'])
                sub_ax7.get_yaxis().set_visible(False)  # 不显示y轴
                sub_ax7.get_xaxis().set_visible(False)  # 不显示x轴

                # 添加单位km
                box = sub_ax7.get_position()
                rect = [box.xmax + 0.008, box.ymax, 0.1, 0.05]
                axText = fig.add_axes(rect, frameon=False)  # 是否显示标签框
                axText.get_yaxis().set_visible(False)  # 不显示y轴刻度
                axText.get_xaxis().set_visible(False)  # 不显示x轴刻度

                fontdict = {'family': property['fontFamily'],  # 字体样式
                            'weight': 5,  # 字体宽度
                            'color': [float(x) / 255.0 for x in property['textColor'].split(',')]  # 字体颜色
                            }
                axText.text(s=property['unitLabel'], x=0, y=0, transform=axText.transAxes, fontdict=fontdict)
            return True
        except:
            print('比例尺绘制失败')
            return False

    def ClassifiedContourf(self, ax, data, colorlevels, colors):
        """
        单波段分级赋色

        colorlevels : 分段刻度

        colors : 区间颜色

        labels : 区间标签
        """
        try:
            data_map = mcolors.ListedColormap(colors)  # 产生颜色映射

            norm = mcolors.BoundaryNorm(colorlevels, data_map.N)  # 生成索引

            XSize = data.shape[1]
            YSize = data.shape[0]
            startLon = self.geotrans[0] + self.geotrans[1] * 0.5
            endLon = startLon + self.geotrans[1] * XSize
            endLat = self.geotrans[3] + self.geotrans[5] * 0.5
            startLat = endLat + self.geotrans[5] * YSize

            olon = np.linspace(startLon, endLon, XSize, endpoint=True)
            olat = np.linspace(endLat, startLat, YSize, endpoint=True)
            contf = ax.contourf(olon, olat, data, levels=colorlevels, cmap=data_map, norm=norm, zorder=5)

            return contf
        except:
            print("SinglebandPseudocolor IS Faild")
            return

    def ClassifiedImshow(self, ax, data, colorlevels, colors):
        """
        imshow参数说明:
            data : 待绘制数组
            cmap : 颜色表
            aspect :  {‘equal’，’auto’} 控制轴的纵横比, 像素是否为正方形
            interpolation : 插值方法
                ’none’, ‘nearest’, ‘bilinear’, ‘bicubic’,’spline16′, ‘spline36’, ‘hanning’, ‘hamming’,
                ‘hermite’, ‘kaiser’, ‘quadric’, ‘catrom’, ‘gaussian’, ‘bessel’, ‘mitchell’, ‘sinc’,’lanczos’.
            origin : {‘upper’, ‘lower’}
                将数组的[0,0]索引放在轴的左上角或左下角。‘upper’通常用于矩阵和图像。

        """
        try:
            data_map = mcolors.ListedColormap(colors)  # 产生颜色映射
            norm = mcolors.BoundaryNorm(colorlevels, data_map.N)  # 生成索引

            vmin = self.minV
            vmax = self.maxV
            data[data < vmin] = np.nan
            data[data > vmax] = np.nan

            XSize = data.shape[1]
            YSize = data.shape[0]
            startLon = self.geotrans[0] - self.geotrans[1] * 0.5
            endLon = self.geotrans[0] + self.geotrans[1] * (XSize - 0.5)
            endLat = self.geotrans[3] + self.geotrans[5] * 0.5
            startLat = self.geotrans[3] + self.geotrans[5] * (YSize - 0.5)
            extent = [startLon, endLon, startLat, endLat]

            imshow = ax.imshow(data, cmap=data_map,
                               norm=norm,
                               aspect='auto',
                               interpolation='none',
                               origin='upper',
                               extent=extent,
                               resample=True,
                               transform=ccrs.PlateCarree(),
                               )
            return imshow
        except:
            print("专题图绘制失败")
            return

    def AddColorBar(self, fig, ax, data, colorlevels, colors, colorlabels, nrow=2, labelmark=True):
        """
        nrow: legend的行数

        添加Colorbar handle

        pos控制colorbar长度，宽度; shrink暂时不起作用

        控制 colorbar tick
        which: 对主or副坐标轴进行操作
        direction: 可选{‘in’, ‘out’, ‘inout’}刻度线的方向
        length : float, 刻度线的长度
        width : float, 刻度线的宽度
        labelsize : float/str, 刻度值字体大小
        bottom, top, left, right: bool, 分别表示上下左右四边，是否显示刻度线，True为显示

        """
        try:
            # box = ax.get_position()
            nrow = int(nrow)
            box = ax.get_position(original=True)
            orientation = "horizontal"
            shrink = 0.28
            aspect = 5
            pad = 0.24

            if nrow == 0 or nrow == 1:
                maphandle = self.get_none_ax(data, colorlevels, colors)

                pos = [box.xmin, 0.04, 0.30, 0.015]

                cax = fig.add_axes(pos)
                cb = fig.colorbar(maphandle, cax=cax,
                                  orientation=orientation,
                                  shrink=shrink,
                                  aspect=aspect,
                                  pad=pad)

                if labelmark:
                    colorlevels_ = []
                    for idx in range(len(colors)):
                        gab = (colorlevels[idx + 1] - colorlevels[idx]) / 2
                        colorlevels_.append(colorlevels[idx] + gab)
                    cb.set_ticks(colorlevels_)
                    cb.set_ticklabels(colorlabels)
                else:

                    colorlevels = np.array(colorlevels)
                    cb.set_ticks(colorlevels.round(2))
                    cb.set_ticklabels(colorlevels.round(2))

                cb.ax.tick_params(which='major', direction='in', length=0.1, width=1.0, labelsize=10, left=True,
                                  right=True)
                cb.outline.set_visible(False)  # 去除外边框线
                plt.close()
            else:
                toppad = 0.1
                bottompad = -0.01
                H = box.ymin - bottompad - toppad
                each_h = H / nrow

                legend_num = len(colors)
                each_row_num = int(legend_num / nrow)

                for cur_row in range(nrow):
                    idx_left = int(cur_row * each_row_num)
                    idx_right = int((cur_row + 1) * each_row_num)

                    if cur_row < (nrow - 1):
                        cur_colorlevels = colorlevels[idx_left: idx_right + 1]
                        cur_colors = colors[idx_left: idx_right]
                        cur_colorlabels = colorlabels[idx_left: idx_right]
                    else:
                        cur_colorlevels = colorlevels[idx_left:]
                        cur_colors = colors[idx_left:]
                        cur_colorlabels = colorlabels[idx_left:]

                    cur_handle = self.get_none_ax(data, cur_colorlevels, cur_colors)

                    pos = [box.xmin, box.ymin - toppad - each_h * cur_row, 0.30, 0.015]

                    cax = fig.add_axes(pos)
                    cb = fig.colorbar(cur_handle, cax=cax,
                                      orientation=orientation,
                                      shrink=shrink,
                                      aspect=aspect,
                                      pad=pad)

                    if labelmark:
                        cur_colorlevels_ = []
                        for idx in range(len(cur_colors)):
                            gab = (cur_colorlevels[idx + 1] - cur_colorlevels[idx]) / 2
                            cur_colorlevels_.append(cur_colorlevels[idx] + gab)
                        cb.set_ticks(cur_colorlevels_)
                        cb.set_ticklabels(cur_colorlabels)
                    else:
                        cur_colorlevels = np.array(cur_colorlevels)
                        cb.set_ticks(cur_colorlevels.round(2))
                        cb.set_ticklabels(cur_colorlevels.round(2))

                    cb.ax.tick_params(which='major', direction='in', length=0.1, width=1.0, labelsize=10, left=True,
                                      right=True)
                    cb.outline.set_visible(False)  # 去除外边框线
                    plt.close()
            return True
        except:
            print("ColorBar添加失败")
            return False

    def AddLegend(self, ax, colors, labels):
        """
        绘制colorbar
        colorlevels : 分段刻度
        colors : 区间颜色
        labels : 区间标签

        mpatches.Rectangle参数说明:
            xy : (float, float) 矩形左下角坐标     不包含后面画布大小
            width : 矩形的宽度   (小于1)
            height : 矩形的高度  (小于1)
            alpha : 矩阵的透明度

            fill : 是否填充
            facecolor : 是否填充矩形
            edgecolor : 边框色
            linewidth : 边框线条宽度
        """
        try:
            handles = []
            for color in colors:
                handle = mpatches.Rectangle((0, 0), 1, 1, facecolor=color, edgecolor=color)
                handles.append(handle)

            box = ax.get_position()

            ax.legend(handles, labels,
                      loc='lower left',  # 控制legend相对位置  与bbox_to_anchor冲突

                      prop='Times New Roman',  # 字体样式
                      fontsize=12,

                      markerscale=1,  # 图例标记与原始标记的相对大小
                      markerfirst=True,  # True mark色框在前

                      frameon=True,  # 是否显示图例边框  控制是否应在图例周围绘制框架
                      fancybox=True,  # 是否将图框边角设为圆形
                      shadow=True,  # 图例边框是否添加阴影
                      framealpha=None,  # 控制图例框架的 Alpha 透明度
                      edgecolor='k',  # Frame edgecolor
                      facecolor=None,  # Frame facecolor

                      ncol=1,  # 图例的列数

                      # borderpad=0.5,  # 图例边框的内边距
                      # labelspacing=0.5,  # 图例条目之间的垂直间距
                      # handlelength=2,  # 图例句柄的长度
                      # handleheight=2， # 图例句柄的高度
                      # handletextpad=0.5，  # 图例句柄和文本之间的间距
                      # borderaxespad=0.5，  #  轴与图例边框之间的距离

                      # columnspacing=0.5，  # 列间距

                      title='图例（mm）',

                      bbox_to_anchor=(0, 0),  # 指定图例在轴的位置
                      )
            return True
        except:
            print("绘制colorbar出错")
            return False

    def shp2clip(self, ax, border, handle):
        """白化处理"""
        try:
            vertices = []
            codes = []

            pts = border.points
            prt = list(border.parts) + [len(pts)]
            for i in range(len(prt) - 1):
                for j in range(prt[i], prt[i + 1]):
                    vertices.append((pts[j][0], pts[j][1]))
                codes += [Path.MOVETO]
                codes += [Path.LINETO] * (prt[i + 1] - prt[i] - 2)
                codes += [Path.CLOSEPOLY]
            clip = Path(vertices, codes)
            clip = PathPatch(clip, transform=ax.transData)

            for collection in handle.collections:
                collection.set_clip_path(clip)
            return True
        except:
            print("白化失败")
            return False

    def TransparentMap(self, TransparentPath, border):
        try:
            ShpExtent = self.DataFrame['ShpExtent']
            ratio = (ShpExtent['xmax'] - ShpExtent['xmin']) / (ShpExtent['ymax'] - ShpExtent['ymin'])

            mapW = self.mapW
            mapH = mapW / ratio
            figsize = (mapW, mapH)

            fig = plt.figure(figsize=figsize, dpi=100, frameon=False)

            ax = fig.add_axes([0, 0, 1, 1], frameon=False, projection=ccrs.PlateCarree())

            # [minLon, maxLon, minLat, maxLat]
            extent = [ShpExtent['xmin'], ShpExtent['xmax'], ShpExtent['ymin'], ShpExtent['ymax']]
            ax.set_extent(extent, crs=ccrs.PlateCarree())

            # ax的显隐设置
            ax.axison = False

            handle = self.ClassifiedContourf(ax, self.data, self.colorlevels, self.colors)
            # handle = self.ClassifiedImshow(ax, self.data, self.colorlevels, self.colors)

            # 裁剪
            self.shp2clip(ax, border, handle)
            fig.savefig(TransparentPath, dpi=fig.dpi, transparent=True)
            plt.close()
            return True
        except:
            print('全透图生产失败')
            return False

    def AddSysFeature(self, ax):
        """添加系统内置矢量"""

        # Plot border lines
        for line in self.borders:
            ax.plot(line[0::2], line[1::2], "-", lw=1., color="k", transform=ccrs.Geodetic())

        ax.add_feature(cfeature.OCEAN.with_scale("50m"))
        ax.add_feature(cfeature.LAND.with_scale("50m"))
        ax.add_feature(cfeature.RIVERS.with_scale("50m"))
        ax.add_feature(cfeature.LAKES.with_scale("50m"))
        # fig.canvas.draw()

    def AddSouthChinaSea(self, fig):
        sub_ax = fig.add_axes([0.05, 0.18, 0.14, 0.155], projection=ccrs.PlateCarree())
        sub_ax.set_extent([105, 125, 0, 25], crs=ccrs.PlateCarree())

        for line in self.borders:
            sub_ax.plot(line[0::2], line[1::2], "-", lw=1., color="k", transform=ccrs.Geodetic())

        sub_ax.add_feature(cfeature.OCEAN.with_scale("50m"))
        sub_ax.add_feature(cfeature.LAND.with_scale("50m"))
        sub_ax.add_feature(cfeature.RIVERS.with_scale("50m"))
        sub_ax.add_feature(cfeature.LAKES.with_scale("50m"))

    def DrivenPageMap(self):
        """DrivenPage专题图"""
        try:
            sf = shapefile.Reader(self.shpFile)  # encoding参数读取中文 , encoding='gb18030'
            borders = sf.shapes()  # 几何信息

            print(self.shpFile.replace("\\", '/') + " : " + str(len(borders)))
            time.sleep(0.5)
            for i in tqdm(range(len(borders))):
                border = sf.shape(i)  # 第i个shape类的点集信息
                x, y = zip(*border.points)

                # 01 获取当前feature下的属性表信息
                id = sf.record(i).ID  # 第i个shape类属性表中ID字段的信息
                name = sf.record(i).NAME  # 第i个shape类属性表中NAME字段的信息
                if id not in self.staMap.keys():
                    continue

                # print(id, name)
                # 02 重新计算ShpExtent, MapExtent, figsize
                bbox = border.bbox  # 第i个shape类的 左下角 Lon,Lat  +   右上角 Lon,Lat
                self.DataFrame, self.PageSetup = OsgeoTools.CalPageLayout(bbox, self.Margin, self.mapW,
                                                                          self.printResolution, self.DataFrame,
                                                                          self.PageSetup)

                # 03绘图
                # 添加画布
                fig = self.AddPage(self.PageSetup, self.printResolution)
                # 添加绘图区
                ax = self.AddMap(fig, self.DataFrame, self.MapGrid, self.shpMark)
                # 添加标题
                flag = self.AddTitle(fig, self.Title, name)
                if flag is False:
                    return False
                # 添加期次
                self.AddIssue(fig, self.Issue, self.issueLabelText)
                if flag is False:
                    return False
                # 添加Label
                flag = self.AddLabel(fig, self.Label)
                if flag is False:
                    return False
                # 添加Picture
                flag = self.AddPicture(fig, self.Picture)
                if flag is False:
                    return False
                # 添加矢量
                flag = self.AddAtlas(ax, self.Atlas)
                if flag is False:
                    return False
                # 添加城市标注
                flag = self.AddAnnotation(ax, self.Annotation, border.points)
                if flag is False:
                    return False
                # 添加指北针
                flag = self.AddNorthArrow(ax, self.NorthArrow)
                if flag is False:
                    return False
                # 添加比例尺
                flag = self.AddScalBar(fig, self.ScaleBar)
                if flag is False:
                    return False
                # tif渲染
                handle = self.ClassifiedContourf(ax, self.data, self.colorlevels, self.colors)
                # handle = self.ClassifiedImshow(ax, self.data, self.colorlevels, self.colors)
                # 添加colorbar
                flag = self.AddColorBar(fig, ax, self.data, self.colorlevels, self.colors, self.colorlabels)
                if flag is False:
                    return False
                # 绘制当前矢量
                # ax.plot(x, y, '-', lw=1.0, color='k', transform=ccrs.Geodetic())
                # 白化
                flag = self.shp2clip(ax, border, handle)
                if flag is False:
                    return False
                # 保存
                if BaseFile.isFileOrDir(os.path.join(self.outDir, id)) != BaseFile.ISDIR:
                    BaseFile.creatDir(os.path.join(self.outDir, id))
                regionPath = os.path.join(self.outDir, id + "/" + id + ".jpg")
                fig.savefig(regionPath, dpi=fig.dpi)
                plt.close()
                # 全透图
                transparentPath = os.path.join(self.outDir, id + "/" + id + "_transparent.png")
                flag = self.TransparentMap(transparentPath, border)
                if flag is False:
                    return False

                # 返回文件列表
                if BaseFile.isFileOrDir(regionPath) == BaseFile.ISFILE:
                    self.returnJPGMap[id] = regionPath
                if BaseFile.isFileOrDir(transparentPath) == BaseFile.ISFILE:
                    self.returnPNGMap[id] = transparentPath
            time.sleep(0.5)
            return True
        except:
            return False

    def NoDrivenPageMap(self, name, id, level):
        """非DrivenPage专题图绘制 注意level，id，name"""
        pass

    def get_none_ax(self, data, colorlevels, colors):
        """获取一个渲染的轴ax"""
        fig, ax = plt.subplots()

        data_map = mcolors.ListedColormap(colors)  # 产生颜色映射

        norm = mcolors.BoundaryNorm(colorlevels, data_map.N)  # 生成索引

        XSize = data.shape[1]
        YSize = data.shape[0]

        olon = np.linspace(0, XSize, XSize, endpoint=True)
        olat = np.linspace(0, YSize, YSize, endpoint=True)
        contf = ax.contourf(olon, olat, data, levels=colorlevels, cmap=data_map, norm=norm, zorder=5)

        return contf
