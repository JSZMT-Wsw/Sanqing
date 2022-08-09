# encoding: utf-8
"""
@author: DYX
@file: ColorTrans.py
@time: 2020/10/15 15:40
@desc:
"""


class ColorTrans:
	@staticmethod
	# RGB格式颜色转换为16进制颜色格式
	def RGB_to_Hex(rgb):
		RGB = rgb.split(',')  # 将RGB格式划分开来
		color = '#'
		for i in RGB:
			num = int(i)
			# 将R、G、B分别转化为16进制拼接转换并大写  hex() 函数用于将10进制整数转换成16进制，以字符串形式表示
			color += str(hex(num))[-2:].replace('x', '0').upper()
		return color
	
	@staticmethod
	# 16进制颜色格式颜色转换为RGB格式
	def Hex_to_RGB(hex):
		r = int(hex[1:3], 16)
		g = int(hex[3:5], 16)
		b = int(hex[5:7], 16)
		rgb = str(r) + ',' + str(g) + ',' + str(b)
		return rgb
