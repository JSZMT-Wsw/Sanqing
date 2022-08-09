# encoding: utf-8
"""
@author: DYX
@file: AddMap.py
@time: 2020/10/14 11:23
@desc:
"""
import math
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter


def AddMap(fig, DataFrame, MapGrid):
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
		                  projection=ccrs.PlateCarree()
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
		ax.get_yaxis().set_visible(False)  # 不显示y轴
		ax.get_xaxis().set_visible(False)  # 不显示x轴
		
		# ax的显隐设置
		ax.axison = True
		
		# 绘图框边缘线设置  注:ax.spines['left'].set_color() 不起作用，只能用geo关键字
		ax.spines['geo'].set_color(DataFrame['FrameColor'])
		ax.spines['geo'].set_linewidth(DataFrame['outlineWidthM'])
		ax.spines['geo'].set_linestyle('--')
		
		# 添加经纬网
		ax = ModifyGrid(ax, DataFrame, MapGrid)  # 注：在添加经纬网之后，此时的rect已经变了，因为有经纬度标注
		
		if not (ax) is None:
			return ax
		else:
			return ax
	except:
		print("绘图区设置错误")
		return


def ModifyGrid(ax, DataFrame, MapGrid):
	"""
	经纬网绘制及标注
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
		
		gab = int(MapGrid['gridFrameWidth'])
		# xticks = list(range(int(minLon), int(maxLon + 1), gab))
		# yticks = list(range(int(minLat), int(maxLat + 1), gab))
		xticks = list(range(math.ceil(minLon), math.floor(maxLon + 1), gab))
		yticks = list(range(math.ceil(minLat), math.floor(maxLat + 1), gab))
		
		# 绘制经纬网格
		color = [x / 255 for x in MapGrid['gridFramePenColor']]
		ax.gridlines(xlocs=xticks, ylocs=yticks,
		             linestyle='--',
		             lw=MapGrid['gridFramePenThickness'],
		             color=color)
		
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
