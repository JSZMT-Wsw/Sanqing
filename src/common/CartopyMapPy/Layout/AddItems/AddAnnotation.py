# encoding: utf-8
"""
@author: DYX
@file: AddAnnotation.py
@time: 2020/10/19 10:09
@desc:
"""


def AddAnnotation(ax, Annotation):
	"""添加城市标注"""
	
	try:
		for num, property in Annotation.items():
			lon, lat = float(property['lon']), float(property['lat'])
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
			
			ax.scatter(lon, lat, marker=marker, s=s, color=color)
			ax.text(lon - 0.09, lat + 0.05, property['name'], fontdict=fontdict)
		return True
	except:
		print("城市标注添加出错")
		return False
