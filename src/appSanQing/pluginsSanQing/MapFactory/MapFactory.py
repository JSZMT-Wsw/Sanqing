# encoding: utf-8
"""
@author: DYX
@file: MapFactory.py
@time: 2020/10/19 17:05
@desc:
"""


from src.appSanQing.pluginsSanQing.MapFactory.Map_AODDB_H8_AHI import Map_AODDB_H8_AHI
from src.appSanQing.pluginsSanQing.MapFactory.Map_AOD_H8_AHI import Map_AOD_H8_AHI
from src.appSanQing.pluginsSanQing.MapFactory.Map_PM25_H8_AHI import Map_PM25_H8_AHI
from src.appSanQing.pluginsSanQing.MapFactory.Map_PM10_H8_AHI import Map_PM10_H8_AHI
from src.appSanQing.pluginsSanQing.MapFactory.Map_HAZE_H8_AHI import Map_HAZE_H8_AHI
from src.appSanQing.pluginsSanQing.MapFactory.Map_O3_S5P_TROPOMI import Map_O3_S5P_TROPOMI
from src.appSanQing.pluginsSanQing.MapFactory.Map_NO2_S5P_TROPOMI import Map_NO2_S5P_TROPOMI
from src.appSanQing.pluginsSanQing.MapFactory.Map_SO2_S5P_TROPOMI import Map_SO2_S5P_TROPOMI
from src.appSanQing.pluginsSanQing.MapFactory.Map_DUST_H8_AHI import Map_DUST_H8_AHI

from src.appSanQing.pluginsSanQing.MapFactory.Map_AODDB_H8_AHI_COMPOSE import Map_AODDB_H8_AHI_COMPOSE
from src.appSanQing.pluginsSanQing.MapFactory.Map_PM25_H8_AHI_COMPOSE import Map_PM25_H8_AHI_COMPOSE
from src.appSanQing.pluginsSanQing.MapFactory.Map_PM10_H8_AHI_COMPOSE import Map_PM10_H8_AHI_COMPOSE
from src.appSanQing.pluginsSanQing.MapFactory.Map_O3_S5P_TROPOMI_COMPOSE import Map_O3_S5P_TROPOMI_COMPOSE
from src.appSanQing.pluginsSanQing.MapFactory.Map_NO2_S5P_TROPOMI_COMPOSE import Map_NO2_S5P_TROPOMI_COMPOSE
from src.appSanQing.pluginsSanQing.MapFactory.Map_SO2_S5P_TROPOMI_COMPOSE import Map_SO2_S5P_TROPOMI_COMPOSE


class MapFactory:
    """出图函数插件工厂"""

    def __init__(self):
        self.name = "MapFactory"

    def getPlugin(self, mapInfo):
        """"""
        try:
            mapObj = None

            plugainName = mapInfo.getPlugainName()

            if plugainName == "AODDB_H8_AHI":
                mapObj = Map_AODDB_H8_AHI(mapInfo)
            if plugainName == "AOD_H8_AHI":
                mapObj = Map_AOD_H8_AHI(mapInfo)
            elif plugainName == "PM25_H8_AHI":
                mapObj = Map_PM25_H8_AHI(mapInfo)
            elif plugainName == "PM10_H8_AHI":
                mapObj = Map_PM10_H8_AHI(mapInfo)
            elif plugainName == "HAZE_H8_AHI":
                mapObj = Map_HAZE_H8_AHI(mapInfo)
            elif plugainName == "O3_S5P_TROPOMI":
                mapObj = Map_O3_S5P_TROPOMI(mapInfo)
            elif plugainName == "NO2_S5P_TROPOMI":
                mapObj = Map_NO2_S5P_TROPOMI(mapInfo)
            elif plugainName == "DUST_H8_AHI":
                mapObj = Map_DUST_H8_AHI(mapInfo)
            elif plugainName == "SO2_S5P_TROPOMI":
                mapObj = Map_SO2_S5P_TROPOMI(mapInfo)

            if plugainName == "AODDB_H8_AHI_COMPOSE":
                mapObj = Map_AODDB_H8_AHI_COMPOSE(mapInfo)
            elif plugainName == "PM25_H8_AHI_COMPOSE":
                mapObj = Map_PM25_H8_AHI_COMPOSE(mapInfo)
            elif plugainName == "PM10_H8_AHI_COMPOSE":
                mapObj = Map_PM10_H8_AHI_COMPOSE(mapInfo)
            elif plugainName == "O3_S5P_TROPOMI_COMPOSE":
                mapObj = Map_O3_S5P_TROPOMI_COMPOSE(mapInfo)
            elif plugainName == "NO2_S5P_TROPOMI_COMPOSE":
                mapObj = Map_NO2_S5P_TROPOMI_COMPOSE(mapInfo)
            elif plugainName == "SO2_S5P_TROPOMI_COMPOSE":
                mapObj = Map_SO2_S5P_TROPOMI_COMPOSE(mapInfo)

            return mapObj
        except:
            print("绘图对象获取失败")
            return
