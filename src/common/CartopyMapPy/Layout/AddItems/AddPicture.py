# encoding: utf-8
"""
@author: DYX
@file: AddPicture.py
@time: 2020/10/19 9:49
@desc:
"""

import matplotlib.image as mpimg


def AddPicture(fig, Picture):
	"""添加图片 控制宽度百分比即可"""
	
	try:
		for num, attribute in Picture.items():
			
			# 图片相对长、宽
			img = mpimg.imread(attribute['file'])
			imgW = img.shape[1] / 1000
			imgH = img.shape[0] / 1000
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
			
			axPic.imshow(img, extent=[0, imgRW, 0, imgRH])  # imshow()绘图，会有0.5个像素的偏差
		
		return True
	except:
		print("添加图片失败")
		return False
