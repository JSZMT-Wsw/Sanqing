# encoding: utf-8
"""
@author: DYX
@file: AddPage.py
@time: 2020/10/16 18:27
@desc:
"""
import matplotlib.pyplot as plt
from pylab import mpl

mpl.rcParams['font.sans-serif'] = 'FangSong'  # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题


def AddPage(PageSetup, printResolution):
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
