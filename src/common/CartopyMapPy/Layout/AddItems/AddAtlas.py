# encoding: utf-8
"""
@author: DYX
@file: AddAtlas.py
@time: 2020/10/19 9:57
@desc:
"""
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader


def AddAtlas(ax, Altas):
	"""添加矢量"""
	
	try:
		for num, layerPropertys in Altas.items():
			filename = layerPropertys['file']
			reader = Reader(filename)
			
			feature = cfeature.ShapelyFeature(reader.geometries(), ccrs.PlateCarree(),
			                                  facecolor=layerPropertys['BackgroundColor'],
			                                  edgecolor=layerPropertys['FrameColor'])
			linewidth = float(layerPropertys['outlineWidthM'])
			ax.add_feature(feature, linewidth=linewidth, zorder=0)
		return True
	except:
		print("添加矢量失败")
		return
