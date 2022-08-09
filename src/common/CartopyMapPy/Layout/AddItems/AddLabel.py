# encoding: utf-8
"""
@author: DYX
@file: AddLabel.py
@time: 2020/10/16 18:49
@desc:
"""


def AddLabel(fig, Label):
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
			            transform=axText.transAxes)
		return True
	except:
		print('标签添加失败')
		return
