# encoding: utf-8
"""
@author: DYX
@file: Map_DUST_H8_AHI.py
@time: 2020/10/19 17:07
@desc:
"""
from osgeo import gdal
import cartopy.crs as ccrs
import numpy as np
import cartopy.feature as cfeature
from shapely.geometry import Polygon, Point
from src.common.CartopyMapPy.Layout.Process.BaseProcess import BaseProcess
import os
import matplotlib.pyplot as plt
import shapefile
from pylab import mpl
from tqdm import tqdm
from src.common.CartopyMapPy.Layout.tools.OsgeoTools import OsgeoTools
from src.common.CartopyMapPy.Layout.tools.ColorTrans import ColorTrans
from src.common.utils.FileUtil import BaseFile

mpl.rcParams['font.sans-serif'] = 'FangSong'  # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题


def readTifByShp(tifFile, shpFile, key, value, scale):
    """矢量数据裁剪"""
    dataset = gdal.Open(tifFile)
    XSize = dataset.RasterXSize
    YSize = dataset.RasterYSize

    scale = int(scale)

    dsScale = gdal.Warp("", dataset, format="MEM",
                        width=XSize * scale, height=YSize * scale,
                        resampleAlg=gdal.GRA_Bilinear, )

    cutline_where_args = key + " = " + "\'" + str(value) + "\'"  # filter continue
    output_bounds_args = None
    # outDs = gdal.Warp("", dsScale, format="MEM", cutlineDSName=shpFile,
    #                   cutlineWhere=cutline_where_args, outputBounds=output_bounds_args,
    #                   width=XSize * scale, height=YSize * scale,
    #                   resampleAlg=gdal.GRA_Bilinear,
    #                   )
    outDs = gdal.Warp("", dsScale, format="MEM",
                      cutlineWhere=cutline_where_args, outputBounds=output_bounds_args,
                      width=XSize * scale, height=YSize * scale,
                      resampleAlg=gdal.GRA_Bilinear,
                      )
    data, geotrans = OsgeoTools.read_tiff(outDs, 1)
    return data, geotrans

class Map_DUST_H8_AHI(BaseProcess):
    """AOD_H8_AHI绘图"""

    def __init__(self, mapInfo):
        BaseProcess.__init__(self, mapInfo)

    def getData(self, tifFile, shpFile, key, value, scale=1):
        """数据获取并插值处理"""
        try:
            data, geotrans = readTifByShp(tifFile, shpFile, key, value, scale)
            return data, geotrans
        except Exception as e:
            print(e)
            print("数据获取失败")
            return
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
                self.getPageParams(bbox)

                # 04 绘图
                fig = self.PlotComp(id, name, border, bbox, data, geotrans)
                # 保存
                if BaseFile.isFileOrDir(os.path.join(self.outDir, id)) != BaseFile.ISDIR:
                    BaseFile.creatDir(os.path.join(self.outDir, id))
                regionPath = os.path.join(self.outDir, id + "/" + id + ".png")
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
    def getPageParams(self, bbox):
        """"""
        try:
            if bbox[3]-bbox[1] > 30:
                bbox = [74, 21.14357899999999, 134.09567000000027, 53.56326900000016]
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
        # 添加矢量
        self.AddAtlas(ax, self.Atlas)
        # 添加城市标注
        self.AddAnnotation(ax, self.Annotation, border.points)
        # # 添加指北针
        self.AddNorthArrow(ax, self.NorthArrow)
        # 颜色渐进
        self.getColors(data, self.colors, self.colorlevels)
        # tif渲染
        self.ClassifiedImshow(ax, data, geotrans, self.colorlevelsDrow, self.colorsDrow)
        box = ax.get_position(original=True)
        self.AddPicture(fig, self.Picture)
        # 添加比例尺
        self.AddScalBar(fig, self.ScaleBar)
        # 添加期次
        self.AddIssue(fig, self.Issue, self.issueLabelText)
        # 添加标题
        self.AddTitle(fig, self.Title, name)
        # 添加Label
        self.AddLabel(fig, self.Label)
        # # 添加ColorBar
        self.AddColorBar(fig, ax, data, self.colorlevels, self.colors, self.colorlabels)
        # 添加南海子图
        self.AddSouthChinaSea(fig, ax, self.DataFrame['Extent'])

        return fig
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

            label = (Title['labelText'])
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
            ax.set_xticks([])
            ax.set_yticks([])

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

    def AddSysFeature(self, ax):
        """添加系统内置feature, LAND颜色覆盖了ax的DataFrame['BackgroundColor']"""
        try:
            ax.add_feature(cfeature.OCEAN.with_scale('50m'))
            # ax.add_feature(cfeature.LAND.with_scale('50m'))
            ax.add_feature(cfeature.LAKES.with_scale('50m'))
            ax.add_feature(cfeature.RIVERS.with_scale("50m"))
        except Exception as e:
            print(e)
            print("添加系统内置feature失败")
            return
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
                minBarWidth = maxBarWidth / 4
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
                pos3 = [pos2[0] + pos2[2], loc_y, minBarWidth*2, BarHeight]
                # pos4 = [pos3[0] + pos3[2], loc_y, minBarWidth, BarHeight]
                #
                # pos5 = [pos4[0] + pos4[2], loc_y, minBarWidth * 4, BarHeight]
                # pos6 = [pos5[0] + pos5[2], loc_y, minBarWidth * 4, BarHeight]
                # pos7 = [pos6[0] + pos6[2], loc_y, minBarWidth * 4, BarHeight]
                #
                pos17 = [pos1[0], loc_y, minBarWidth * 4, BarHeight]

                sub_ax17 = fig.add_axes(pos17, frameon=True, facecolor='w')
                sub_ax17.set_xticks(
                    np.array([0, graduat, graduat * 2, graduat * 4]))  # x周刻度
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
                # sub_ax4 = fig.add_axes(pos4, frameon=True, facecolor=property['fillColor2'])
                # sub_ax4.get_yaxis().set_visible(False)  # 不显示y轴
                # sub_ax4.get_xaxis().set_visible(False)  # 不显示x轴
                #
                # sub_ax5 = fig.add_axes(pos5, frameon=True, facecolor=property['fillColor'])
                # sub_ax5.get_yaxis().set_visible(False)  # 不显示y轴
                # sub_ax5.get_xaxis().set_visible(False)  # 不显示x轴
                #
                # sub_ax6 = fig.add_axes(pos6, frameon=True, facecolor=property['fillColor2'])
                # sub_ax6.get_yaxis().set_visible(False)  # 不显示y轴
                # sub_ax6.get_xaxis().set_visible(False)  # 不显示x轴
                #
                # sub_ax7 = fig.add_axes(pos7, frameon=True, facecolor=property['fillColor'])
                # sub_ax7.get_yaxis().set_visible(False)  # 不显示y轴
                # sub_ax7.get_xaxis().set_visible(False)  # 不显示x轴

                # 添加单位km
                box = sub_ax3.get_position()
                rect = [box.xmax + 0.008, box.ymax, 0.1, 0.05]
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
    def AddSouthChinaSea(self, fig, ax, extent):
        try:
            if extent['xmax'] >= 125 and extent['ymin'] <= 20:
                box = ax.get_position(original=False)
                # sub_ax = fig.add_axes([box.xmin - 0.015, box.ymin + 0.015, 0.14, 0.155], projection=ccrs.PlateCarree())
                sub_ax = fig.add_axes([box.xmax - 0.1405, box.ymin + 0.015, 0.14, 0.155], projection=ccrs.PlateCarree())
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
                tempText = "北京时:" + issueLabelText[0:4] + "-"
            if "月" in Issue['labelText']:
                tempText += str(int(issueLabelText[4:6])) + "-"
            if "日" in Issue['labelText']:
                tempText += str(int(issueLabelText[6:8]))
            if "时" in Issue['labelText']:
                tempText += " " + str(int(issueLabelText[8:10]))
            if "分" in Issue['labelText']:
                tempText += ":" + issueLabelText[10:12]
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
    def AddColorBar(self, fig, ax, data, colorlevels, colors, colorlabels, nrow=1, labelmark=True, pos=None):
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
            pad = 0.3

            if pos is None:
                # pos = [box.xmin+0.01, 0.2, 0.046, 0.022]
                # pos = [box.xmin + 0.01, 0.23, 0.046, 0.022]
                # pos = [box.xmin + 0.01, 0.19, 0.046, 0.022]
                pos = [box.xmin + 0.01, 0.035, 0.14, 0.03]

            toppad = 0.06
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
                    # cb.set_ticklabels(cur_colorlabels)
                cur_handle1 = self.get_none_ax(data, cur_colorlevels, cur_colors)
                cur_pos1 = [pos[0], box.ymin - toppad - each_h * (cur_row + 1), pos[2], 0]
                # cur_pos1 = [pos[0], box.ymin - toppad - each_h * (cur_row + 1)+0.024, pos[2], 0]
                cax1 = fig.add_axes(cur_pos1)
                cb1 = fig.colorbar(cur_handle1, cax=cax1, orientation=orientation, shrink=shrink, aspect=aspect,
                                  pad=pad)
                if labelmark:
                    cb1.set_ticks(cur_colorlevels_)
                    cb1.set_ticklabels(cur_colorlabels)
                    # num = 0
                    # for items in cur_colorlabels:
                    #     if items != '':
                    #         cb1.set_label(items, x=cur_colorlevels_[num], y=pos[1], color='red')
                    #         num = num + 1
                    # # cb.set_label(cur_colorlabels, x=pos[0]+0.5, y=pos[1]+0.5, color='red')
                else:
                    cur_colorlevels = np.array(cur_colorlevels)
                    cb.set_ticks(cur_colorlevels.round(2))
                    cb.set_ticklabels(cur_colorlevels.round(2))

                cb.ax.tick_params(which='major', direction='in', length=0.1, width=1.0, labelsize=10, left=True,
                                  right=True, labelcolor='none')
                cb.outline.set_visible(False)  # 去除外边框线
                cb1.ax.tick_params(which='major', direction='in', length=0.1, width=1.0, labelsize=14, left=True,
                                  right=True, labelcolor='black')
                cb1.outline.set_visible(False)  # 去除外边框线
                plt.close()
        except Exception as e:
            print(e)
            print("ColorBar添加失败")
            return
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
                if keyVal == '100000000000':
                    pos = [box.xmin + 0.01, 0.19, 0.46, 0.022]
                elif keyVal == '370000000000':
                    pos = [box.xmin, 0.02, 0.46, 0.03]
                else:
                    pos = [box.xmin, 0.025, 0.46, 0.022]
                # pos = [box.xmin+0.01, 0.245, 0.46, 0.022]
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

                # 拉伸方法一 常规情况下用方法一即可
                # rgb_bands = np.array([r, g, b])
                # rgb_bands = self.stretch_im(rgb_bands, 2, flag=False)
                # 拉伸方法二
                # R = self.stretch_im(r, 2, flag=True)
                # G = self.stretch_im(g, 2, flag=False)
                # B = self.stretch_im(b, 2, flag=False)
                # rgb_bands = np.array([R, G, B])
                if r.min()<0:
                    R = self.stretch_im(r, 2, flag=True)
                    G = self.stretch_im(g, 2, flag=False)
                    B = self.stretch_im(b, 2, flag=False)
                    rgb_bands = np.array([R, G, B])
                else:
                    rgb_bands = np.array([r, g, b])
                    rgb_bands = self.stretch_im(rgb_bands, 2, flag=False)

                # 数据类型转换UINT8
                rgb_bands = self.bytescale(rgb_bands)

                # 添加透明度通道
                # rgb_bands = np.asarray([rgb_bands[0], rgb_bands[1], rgb_bands[2], A])

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
    def AddAnnotation(self, ax, Annotation, pointsList):
        """
        添加城市标注
        第i个shape类的 左下角 Lon,Lat  +   右上角 Lon,Lat
        """

        try:
            poly = Polygon(pointsList)
            if len(pointsList)> 5000 and len(pointsList) < 20000:
                for num, property in Annotation.items():
                    lon, lat = float(property['lon']), float(property['lat'])

                    point = Point(lon, lat)
                    flag = point.within(poly)
                    # if not (flag):
                    #     continue

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
            else:
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