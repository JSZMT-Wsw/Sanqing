# encoding: utf-8
"""
@author: DYX
@file: BaseProcess.py
@time: 2020/10/20 13:56
@desc:
"""
import os
from osgeo import gdal
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors as mcolors
import matplotlib.image as mpimg
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import shapefile
from cartopy.io.shapereader import Reader
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from pylab import mpl
from shapely.geometry import Polygon, Point
from tqdm import tqdm
import math
from matplotlib.colors import LinearSegmentedColormap
from skimage import exposure
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
``Contourf	zorder=10
``比例尺		zorder=95
"""


class BaseProcess:
    """出图函数基类"""

    def __init__(self, mapInfo):
        LayoutDir = os.path.dirname(os.path.dirname(__file__))
        self.borderPath = os.path.dirname(LayoutDir) + "/depend/Sysborder/CN-border-La.dat"
        self.borders = None  # 系统内置边界

        self.mapW = 10  # 中间地图大小 一般给定10
        self.transparent = True

        self.returnJPGMap = {}  # 输出文件
        self.returnPNGMap = {}  # 输出文件

        # 配置文件传入信息参数   colorBar用到
        self.colorlevels = mapInfo.getColorLevels()  # 分级刻度  包含两端点
        self.colors = mapInfo.getColors()  # 分级区间颜色
        self.colorlabels = mapInfo.getColorLabels()  # 分级区间标签

        # 绘图时的配色区间和颜色值
        self.colorlevelsDrow = None
        self.colorsDrow = None

        # 算法传入信息参数
        self.tifFile = mapInfo.gettifFile()
        self.lyrMap = mapInfo.getlyrMap()
        self.rgbFileMap = mapInfo.getrgbPseudoMap()
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

        # 颜色RGB转16进制
        # self.colors = [ColorTrans.RGB_to_Hex(x) for x in self.colors]

    def doMap(self):
        if self.drivenPages:
            flag = self.DrivenPageMap()
            if flag:
                return True
        else:
            pass

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
                data, geotrans = self.getData(self.tifFile, self.shpFile, "ID", id)

                # 03  重新计算ShpExtent, MapExtent, figsize
                self.DataFrame, self.PageSetup = OsgeoTools.CalPageLayout(bbox, self.Margin, self.mapW,
                                                                          self.printResolution, self.DataFrame,
                                                                          self.PageSetup)

                # 04 绘图
                fig = self.PlotComp(id, name, border, bbox, data, geotrans)
                # 保存
                if BaseFile.isFileOrDir(os.path.join(self.outDir, id)) != BaseFile.ISDIR:
                    BaseFile.creatDir(os.path.join(self.outDir, id))
                regionPath = os.path.join(self.outDir, id + "/" + id + ".jpg")
                fig.savefig(regionPath, dpi=fig.dpi)
                plt.close()

                # 05 绘制透明图
                transparentPath = os.path.join(self.outDir, id + "/" + id + "_transparent.png")
                self.TransparentMap(data, geotrans, transparentPath)

                # 返回文件列表
                if BaseFile.isFileOrDir(regionPath) == BaseFile.ISFILE:
                    self.returnJPGMap[id] = regionPath
                if BaseFile.isFileOrDir(transparentPath) == BaseFile.ISFILE:
                    self.returnPNGMap[id] = transparentPath

            return True
        except Exception as e:
            print(e)
            return False

    def getData(self, tifFile, shpFile, key, value, scale=2):
        """数据获取并插值处理"""
        try:
            data, geotrans = OsgeoTools.readTifByShp(tifFile, shpFile, key, value, scale)
            return data, geotrans
        except Exception as e:
            print(e)
            print("数据获取失败")
            return

    def getPageParams(self, bbox):
        """"""
        try:
            self.DataFrame, self.PageSetup = OsgeoTools.CalPageLayout(bbox, self.Margin, self.mapW,
                                                                      self.printResolution, self.DataFrame,
                                                                      self.PageSetup)
        except Exception as e:
            print(e)
            print("页面参数重新获取失败")
            return

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
        # 添加Picture
        self.AddPicture(fig, self.Picture)
        # 添加矢量
        self.AddAtlas(ax, self.Atlas)
        # 添加城市标注
        self.AddAnnotation(ax, self.Annotation, border.points)
        # 添加指北针
        self.AddNorthArrow(ax, self.NorthArrow)
        # 添加比例尺
        self.AddScalBar(fig, self.ScaleBar)

        # 分级渲染
        # 颜色渐进
        self.getColors(data, self.colors, self.colorlevels)
        # tif渲染
        self.ClassifiedImshow(ax, data, geotrans, self.colorlevelsDrow, self.colorsDrow)
        # 添加ColorBar
        self.AddColorBar(fig, ax, data, self.colorlevels, self.colors, self.colorlabels)

        # 渐进渲染
        # 颜色渐进
        self.getGradinetColors(self.colors)
        # tif渲染——渐进色渲染
        handle = self.GradinetImshow(ax, data, geotrans, self.colorlevels, self.colorsDrow)
        # 添加ColorBar
        self.AddGradinetColorBar(fig, ax, handle, self.colorlabels)

        # lyrMap叠加渲染
        self.lyrMapImshow(fig, ax, self.lyrMap, id, 1)
        # RGB叠加渲染
        self.rgbMapImshow(ax, self.rgbFileMap)
        # 添加南海子图
        self.AddSouthChinaSea(fig, ax, self.DataFrame['Extent'])

        return fig

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
        except Exception as e:
            print(e)
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
            ax.add_feature(cfeature.OCEAN.with_scale("50m"))
            ax.add_feature(cfeature.LAND.with_scale("50m"))
            ax.add_feature(cfeature.RIVERS.with_scale("50m"))
            ax.add_feature(cfeature.LAKES.with_scale("50m"))
            # ax.background_img(resolution='low')
            # ax.background_img(resolution='high')
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
        except Exception as e:
            print(e)
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
                level = 0.125

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
                         alpha=0.45,
                         zorder=99)

            # 添加标注
            ax.set_xticks(xticks, crs=ccrs.PlateCarree())
            ax.set_yticks(yticks, crs=ccrs.PlateCarree())

            labelsize = MapGrid['annotationFontProperties'][1]  # 标注字体大小
            pad = MapGrid['gridFramePad']  # 标注与框图间隔
            ax.tick_params(labelsize=labelsize, pad=pad, direction="in", right=False, top=False, axis='both')

            fonname = MapGrid['annotationFontProperties'][0]  # 标注字体样式
            labels = ax.get_xticklabels() + ax.get_yticklabels()
            [label.set_fontname(fonname) for label in labels]

            lon_formatter = LongitudeFormatter(zero_direction_label=False)  # zero_direction_label用来设置经度的0度加不加E和W
            lat_formatter = LatitudeFormatter()
            ax.xaxis.set_major_formatter(lon_formatter)  # 给定N, E样式
            ax.yaxis.set_major_formatter(lat_formatter)

            return ax
        except Exception as e:
            print(e)
            print('修改经纬网格出错')
            return

    def AddSysFeature(self, ax):
        """添加系统内置feature, LAND颜色覆盖了ax的DataFrame['BackgroundColor']"""
        try:
            ax.add_feature(cfeature.OCEAN.with_scale('50m'))
            ax.add_feature(cfeature.LAND.with_scale('50m'))
            ax.add_feature(cfeature.LAKES.with_scale('50m'))
            ax.add_feature(cfeature.RIVERS.with_scale("50m"))
        except Exception as e:
            print(e)
            print("添加系统内置feature失败")
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
        except Exception as e:
            print(e)
            print("标题添加失败")
            return

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
        except Exception as e:
            print(e)
            print("期次添加失败")
            return

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
        except Exception as e:
            print(e)
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
        except Exception as e:
            print(e)
            print("添加图片失败")
            return

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

                # if layerPropertys['isoutline'] == "True" or layerPropertys['isoutline'] == "true":
                #     sf = shapefile.Reader(filename)
                #     border = sf.shape(0)
                #
                #     # 添加第三条线
                #     ply = Polygon(border.points)
                #     dilated = ply.buffer(0.1)
                #     clean = dilated.buffer(0)
                #     for idx in range(len(clean)):
                #         line3 = list(clean[idx].exterior.coords)
                #         x = [item[0] for item in line3]
                #         y = [item[1] for item in line3]
                #         ax.plot(x, y, lw=5.0, color=[1, 0.92, 0.69, 0.5],
                #                 linestyle=layerPropertys['linestyle'], zorder=zorder, transform=ccrs.Geodetic())
                #
                #     # 添加第二条内线
                #     ply = Polygon(border.points)
                #     dilated = ply.buffer(0.05)
                #     clean = dilated.buffer(0)
                #     for idx in range(len(clean)):
                #         line2 = list(clean[idx].exterior.coords)
                #         x = [item[0] for item in line2]
                #         y = [item[1] for item in line2]
                #         ax.plot(x, y, lw=2.5, color=[1, 0.83, 0.50, 0.5],
                #                 linestyle=layerPropertys['linestyle'], zorder=zorder, transform=ccrs.Geodetic())
        except Exception as e:
            print(e)
            print("添加矢量失败")
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
        except Exception as e:
            print(e)
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
        except Exception as e:
            print(e)
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
                rect = [box.xmax + 0.008, box.ymax - 0.005, 0.1, 0.05]
                axText = fig.add_axes(rect, frameon=False)  # 是否显示标签框
                axText.get_yaxis().set_visible(False)  # 不显示y轴刻度
                axText.get_xaxis().set_visible(False)  # 不显示x轴刻度

                fontdict = {'family': property['fontFamily'],  # 字体样式
                            'weight': 5,  # 字体宽度
                            'color': [float(x) / 255.0 for x in property['textColor'].split(',')]  # 字体颜色
                            }
                axText.text(s=property['unitLabel'], x=0, y=0, transform=axText.transAxes, fontdict=fontdict)
        except Exception as e:
            print(e)
            print('比例尺绘制失败')
            return False

    def getColors(self, data, colors, colorlevels):
        """获取绘图时的颜色和分级"""
        try:
            new_colors = []
            new_colorlevels = []
            for item, color in enumerate(colors):
                if item < len(colors) - 1:
                    minColor = colors[item]
                    maxColor = colors[item + 1]
                    new_colors.append(minColor)
                    minColor = minColor.split(",")
                    maxColor = maxColor.split(",")

                    minv = colorlevels[item]
                    maxv = colorlevels[item + 1]
                    new_colorlevels.append(minv)

                    idx = np.where((data >= minv) & (data < maxv))
                    tempData = list(set(list(data[idx])))
                    tempData.sort()
                    for each_data in tempData:
                        ratio = (each_data - minv) / (maxv - minv)
                        R = (float(maxColor[0]) - float(minColor[0])) * ratio + float(minColor[0])
                        G = (float(maxColor[1]) - float(minColor[1])) * ratio + float(minColor[1])
                        B = (float(maxColor[2]) - float(minColor[2])) * ratio + float(minColor[2])
                        new_colors.append(str(int(R)) + "," + str(int(G)) + "," + str(int(B)))
                        new_colorlevels.append(each_data)
                else:
                    new_colors.append(color)
                    new_colorlevels.append(colorlevels[item])
                    new_colorlevels.append(colorlevels[item + 1])

            colors = new_colors
            colors = [ColorTrans.RGB_to_Hex(x) for x in colors]
            colorlevels = new_colorlevels

            self.colorsDrow = colors
            self.colorlevelsDrow = colorlevels
        except Exception as e:
            print(e)
            print("颜色获取失败")
            return False

    def ClassifiedImshow(self, ax, data, geotransform, colorlevels, colors, zorder=10):
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

            minVal = colorlevels[0]
            maxVal = colorlevels[-1]
            data[data < minVal] = np.nan
            data[data > maxVal] = np.nan

            XSize = data.shape[1]
            YSize = data.shape[0]
            startLon = geotransform[0] - geotransform[1] * 0.5
            endLon = geotransform[0] + geotransform[1] * (XSize - 0.5)
            endLat = geotransform[3] + geotransform[5] * 0.5
            startLat = geotransform[3] + geotransform[5] * (YSize - 0.5)
            extent = [startLon, endLon, startLat, endLat]

            olon = np.linspace(startLon, endLon, XSize, endpoint=True)
            olat = np.linspace(endLat, startLat, YSize, endpoint=True)

            # ax.imshow(data, cmap=data_map, norm=norm, vmin=minVal, vmax=maxVal, aspect='auto',
            #                    interpolation='none', origin='upper', extent=extent, resample=True,
            #                    transform=ccrs.PlateCarree(),
            #                    zorder=5)

            ax.pcolormesh(olon, olat, data, cmap=data_map, norm=norm, vmin=minVal, vmax=maxVal,
                          transform=ccrs.PlateCarree(),
                          zorder=zorder)
        except Exception as e:
            print(e)
            print("专题图绘制失败")
            return

    def AddColorBar(self, fig, ax, data, colorlevels, colors, colorlabels, nrow=2, labelmark=False, pos=None, id=None):
        """
        nrow: legend的行数  目前只支持1/2

        pos控制colorbar长度，宽度; shrink暂时不起作用

        控制 colorbar tick
        which: 对主or副坐标轴进行操作
        direction: 可选{‘in’, ‘out’, ‘inout’}刻度线的方向
        length : float, 刻度线的长度
        width : float, 刻度线的宽度
        labelsize : float/str, 刻度值字体大小
        bottom, top, left, right: bool, 分别表示上下左右四边，是否显示刻度线，True为显示

        pos: 左侧，底部，长度， 高度(单条)  pos = [box.xmin, 0.035, 0.30, 0.015]  pos = [box.xmin, 0.09, 0.30, 0.015]
        """
        try:
            colors = [ColorTrans.RGB_to_Hex(x) for x in colors]

            nrow = int(nrow)
            box = ax.get_position(original=True)
            orientation = "horizontal"
            shrink = 0.28
            aspect = 5
            pad = 0.24

            if pos is None:
                pos = [box.xmin, 0.030, 0.30, 0.01]

            toppad = 0.05

            if id == '610000000000':
                pos = [box.xmin, 0.0250, 0.30, 0.008]
                toppad = 0.04

            bottompad = pos[1]
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
                cur_pos = [pos[0], box.ymin - toppad - each_h * (cur_row + 1), pos[2], pos[3]]
                cax = fig.add_axes(cur_pos)
                cb = fig.colorbar(cur_handle, cax=cax, orientation=orientation, shrink=shrink, aspect=aspect, pad=pad)

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
        except Exception as e:
            print(e)
            print("ColorBar添加失败")
            return

    def getGradinetColors(self, colors):
        """根据颜色表生成渐进色"""
        try:
            new_colors = [x.split(",") for x in colors]
            new_colors = [[float(y) for y in x] for x in new_colors]
            new_colors = np.array(new_colors)

            data_map = LinearSegmentedColormap.from_list("name", new_colors / 255.0)
            self.colorsDrow = data_map

        except Exception as e:
            print(e)
            print("渐进色带获取失败")
            return False

    def GradinetImshow(self, ax, data, geotransform, colorlevels, colors, zorder=10):
        """
        渐变色渲染tif
        """
        try:

            # minVal = colorlevels[0]
            # maxVal = colorlevels[-1]
            data[data < colorlevels[0]] = np.nan
            minVal = np.nanmin(data)
            maxVal = np.nanmax(data)

            data[data < minVal] = np.nan
            # data[data > maxVal] = np.nan

            XSize = data.shape[1]
            YSize = data.shape[0]
            startLon = geotransform[0] - geotransform[1] * 0.5
            endLon = geotransform[0] + geotransform[1] * (XSize - 0.5)
            endLat = geotransform[3] + geotransform[5] * 0.5
            startLat = geotransform[3] + geotransform[5] * (YSize - 0.5)
            olon = np.linspace(startLon, endLon, XSize, endpoint=True)
            olat = np.linspace(endLat, startLat, YSize, endpoint=True)

            # colors = 'jet'
            colors = 'RdYlGn_r'
            cur_handle = ax.pcolormesh(olon, olat, data, cmap=colors,
                                       vmin=minVal,
                                       vmax=maxVal,
                                       transform=ccrs.PlateCarree(),
                                       zorder=zorder)
            return cur_handle
        except Exception as e:
            print(e)
            print("专题图绘制失败")
            return

    def AddGradinetColorBar(self, fig, ax, im_handle, colorlabels, nrow=1, labelmark=False, pos=None, id=None):
        try:
            box = ax.get_position(original=True)
            orientation = "horizontal"
            shrink = 0.28
            aspect = 5
            pad = 0.24

            if pos is None:
                pos = [box.xmin, 0.030, 0.30, 0.015]

            toppad = 0.06
            bottompad = pos[1]
            H = box.ymin - bottompad - toppad
            each_h = H / nrow

            cur_pos = [pos[0], box.ymin - toppad - each_h * 1, pos[2], pos[3]]
            cax = fig.add_axes(cur_pos)
            cb = fig.colorbar(im_handle, cax=cax, orientation=orientation, shrink=shrink, aspect=aspect, pad=pad)

            minV = float(math.ceil(im_handle.norm.vmin))
            maxV = math.modf(im_handle.norm.vmax)[-1]
            if labelmark:
                cb.set_ticks([minV, maxV])
                cb.set_ticklabels([colorlabels[0], colorlabels[-1]])
            else:
                cb.set_ticks([minV, maxV])
                cb.set_ticklabels([minV, maxV])

            cb.ax.tick_params(which='major', direction='in', length=0.1, width=1.0, labelsize=10, left=True, right=True)
            cb.outline.set_visible(False)  # 去除外边框线
            plt.close()

        except Exception as e:
            print(e)
            print("ColorBar添加失败")
            return

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

    def lyrMapImshow(self, fig, ax, lyrMap, keyVal, scale):
        """叠加tif栅格渲染, 目前只支持一个tif渲染"""
        try:
            for num, lyr in lyrMap.items():
                tifFile = lyr['file']
                data, geotrans = self.getData(tifFile, self.shpFile, "ID", keyVal, scale)

                colorlevels = lyr['Rev']
                colors = lyr['Color']
                colorsRGBA = [ColorTrans.RGB_to_Hex(x) for x in colors]

                self.ClassifiedImshow(ax, data, geotrans, colorlevels, colorsRGBA, zorder=int(lyr['zorder']))

                colorlabels = lyr['Label']
                box = ax.get_position(original=True)
                pos = [box.xmin + 0.04, 0.08, 0.30, 0.015]
                self.AddColorBar(fig, ax, data, colorlevels, colors, colorlabels, nrow=1, labelmark=True, pos=pos)
        except Exception as e:
            print(e)
            print("叠加tif渲染失败")
            return

    def rgbMapImshow(self, ax, rgbFileMap):
        """RGB三通道渲染"""
        try:
            if len(rgbFileMap.keys()) > 0:
                r, geotrans = OsgeoTools.read_tiff(rgbFileMap['file'], 1, scale=1)
                g = OsgeoTools.read_tiff(rgbFileMap['file'], 2, scale=1)[0]
                b = OsgeoTools.read_tiff(rgbFileMap['file'], 3, scale=1)[0]
                ds = gdal.Open(rgbFileMap['file'])
                nodata = ds.GetRasterBand(1).GetNoDataValue()
                del ds
                idx = np.where((r == nodata) & (g == nodata) & (b == nodata))  # 无效值区域
                A = np.full(r.shape, 255)
                A[idx] = 0  # 定义透明度通道, 将无效值区域设置为透明 0

                XSize = r.shape[1]
                YSize = r.shape[0]
                startLon = geotrans[0] - geotrans[1] * 0.5
                endLon = geotrans[0] + geotrans[1] * (XSize - 0.5)
                endLat = geotrans[3] + geotrans[5] * 0.5
                startLat = geotrans[3] + geotrans[5] * (YSize - 0.5)
                extent = [startLon, endLon, startLat, endLat]

                # 拉伸方法一 常规情况下用方法一即可，不考虑图像中小于0的值
                # rgb_bands = np.array([r, g, b])
                # rgb_bands = self.stretch_im(rgb_bands, 2, flag=False)
                # 拉伸方法二
                R = self.stretch_im(r, 2, flag=True)
                G = self.stretch_im(g, 2, flag=False)
                B = self.stretch_im(b, 2, flag=False)
                rgb_bands = np.array([R, G, B])

                # 数据类型转换UINT8
                rgb_bands = self.bytescale(rgb_bands)

                # 添加透明度通道
                rgb_bands = np.asarray([rgb_bands[0], rgb_bands[1], rgb_bands[2], A])

                # 矩阵转置
                rgb_bands = rgb_bands.transpose([1, 2, 0])

                # 绘制
                ax.imshow(rgb_bands, aspect='auto', vmin=0,
                          interpolation='none', origin='upper', extent=extent, resample=True,
                          transform=ccrs.PlateCarree(),
                          zorder=rgbFileMap['zorder'])
        except Exception as e:
            print(e)
            print("三通道渲染失败")
            return

    def stretch_im(self, arr, str_clip, flag=True):
        """
        数据拉伸,提高对比度
        flag=False, 不考虑小于0的值
        flag=True, 考虑小于0的值
        """
        s_min = str_clip
        s_max = 100 - str_clip

        if flag:
            pLow, pHigh = np.percentile(arr, (s_min, s_max))
        else:
            pLow, pHigh = np.percentile(arr[arr > 0], (s_min, s_max))

        # 强度调整
        # skimage.exposure.rescale_intensity(image, in_range='image', out_range='dtype')
        # image：输入
        arr_rescaled = exposure.rescale_intensity(arr, in_range=(pLow, pHigh))

        return arr_rescaled.copy()

    def bytescale(self, data, high=255, low=0, cmin=None, cmax=None):
        """波段数值归一化到[0, 255]"""
        if data.dtype == "uint8":
            return data
        if high > 255:
            raise ValueError("high should be less than or equal to 255.")
        if low < 0:
            raise ValueError("low should be greater than or equal to 0.")
        if high < low:
            raise ValueError("high should be greater than or equal to low.")
        if cmin is None or (cmin < data.min()):
            cmin = float(data.min())
        if (cmax is None) or (cmax > data.max()):
            cmax = float(data.max())
        # Calculate range of values
        crange = cmax - cmin
        if crange < 0:
            raise ValueError("cmax should be larger than cmin.")
        elif crange == 0:
            raise ValueError(
                "cmax and cmin should not be the same value. Please specify "
                "cmax > cmin"
            )
        scale = float(high - low) / crange
        # If cmax is less than the data max, then this scale parameter will create
        # data > 1.0. clip the data to cmax first.
        data[data > cmax] = cmax
        bytedata = (data - cmin) * scale + low

        outdata = (bytedata.clip(low, high) + 0.5).astype("uint8")

        return outdata

    def AddSouthChinaSea(self, fig, ax, extent):
        try:
            if extent['xmax'] >= 125 and extent['ymin'] <= 20:
                box = ax.get_position(original=False)
                sub_ax = fig.add_axes([box.xmin - 0.015, box.ymin + 0.015, 0.14, 0.155], projection=ccrs.PlateCarree())
                # sub_ax = fig.add_axes([box.xmax - 0.1405, box.ymin + 0.015, 0.14, 0.155], projection=ccrs.PlateCarree())
                sub_ax.set_extent([105, 125, 0, 25], crs=ccrs.PlateCarree())

                for line in self.borders:
                    sub_ax.plot(line[0::2], line[1::2], "-", lw=1., color="k", transform=ccrs.Geodetic())

                sub_ax.add_feature(cfeature.OCEAN.with_scale("50m"))
                sub_ax.add_feature(cfeature.LAND.with_scale("50m"))
                sub_ax.add_feature(cfeature.RIVERS.with_scale("50m"))
                sub_ax.add_feature(cfeature.LAKES.with_scale("50m"))
                # sub_ax.background_img(resolution='low')
        except Exception as e:
            print(e)
            print("添加南海子图失败")
            return

    def TransparentMap(self, data, geotrans, TransparentPath):
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

            # 分级图----------
            self.ClassifiedImshow(ax, data, geotrans, self.colorlevelsDrow, self.colorsDrow)
            # 渐变图----------
            # self.GradinetImshow(ax, data, geotrans, self.colorlevels, self.colorsDrow)

            fig.savefig(TransparentPath, dpi=fig.dpi, transparent=True)
            plt.close()
            return True
        except Exception as e:
            print(e)
            print('全透图生产失败')
            return False
