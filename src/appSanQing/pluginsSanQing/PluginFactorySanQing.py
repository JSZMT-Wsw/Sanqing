# -- coding: utf-8 -- 


from src.appSanQing.pluginsSanQing.AODDB_H8_AHI import AODDB_H8_AHI
from src.appSanQing.pluginsSanQing.AOD_H8_AHI import AOD_H8_AHI
from src.appSanQing.pluginsSanQing.PM25_H8_AHI import PM25_H8_AHI
from src.appSanQing.pluginsSanQing.PM10_H8_AHI import PM10_H8_AHI
from src.appSanQing.pluginsSanQing.DUST_SATPY_H8_AHI import DUST_SATPY_H8_AHI
from src.appSanQing.pluginsSanQing.O3_S5P_TROPOMI import O3_S5P_TROPOMI
from src.appSanQing.pluginsSanQing.NO2_S5P_TROPOMI import NO2_S5P_TROPOMI
from src.appSanQing.pluginsSanQing.SO2_S5P_TROPOMI import SO2_S5P_TROPOMI
from src.appSanQing.pluginsSanQing.DUST_H8_AHI import DUST_H8_AHI
from src.appSanQing.pluginsSanQing.HAZE_H8_AHI import HAZE_H8_AHI

from src.appSanQing.pluginsSanQing.AODDB_H8_AHI_COMPOSE import AODDB_H8_AHI_COMPOSE
from src.appSanQing.pluginsSanQing.PM25_H8_AHI_COMPOSE import PM25_H8_AHI_COMPOSE
from src.appSanQing.pluginsSanQing.PM10_H8_AHI_COMPOSE import PM10_H8_AHI_COMPOSE
from src.appSanQing.pluginsSanQing.O3_S5P_TROPOMI_COMPOSE import O3_S5P_TROPOMI_COMPOSE
from src.appSanQing.pluginsSanQing.NO2_S5P_TROPOMI_COMPOSE import NO2_S5P_TROPOMI_COMPOSE
from src.appSanQing.pluginsSanQing.SO2_S5P_TROPOMI_COMPOSE import SO2_S5P_TROPOMI_COMPOSE

from src.common.process.PluginFactory import PluginFactory


class PluginFactorySQ(PluginFactory):
    '''
    产品算法插件工厂
    '''

    def __init__(self):
        PluginFactory.__init__(self)
        self.name = "PluginFactoryJN"

    def getPlugin(self, pluginInfo):
        '''
        获取算法对象
        '''
        try:
            if pluginInfo is None:
                return

            pluginObj = None

            pluginName = pluginInfo.getPluginName().upper()
            # 大气
            if pluginName == "AODDB_H8_AHI":
                pluginObj = AODDB_H8_AHI(pluginInfo)
            if pluginName == "AOD_H8_AHI":
                pluginObj = AOD_H8_AHI(pluginInfo)
            elif pluginName == "PM25_H8_AHI":
                pluginObj = PM25_H8_AHI(pluginInfo)
            elif pluginName == "PM10_H8_AHI":
                pluginObj = PM10_H8_AHI(pluginInfo)
            elif pluginName == "DUST_SATPY_H8_AHI":
                pluginObj = DUST_SATPY_H8_AHI(pluginInfo)
            elif pluginName == "O3_S5P_TROPOMI":
                pluginObj = O3_S5P_TROPOMI(pluginInfo)
            elif pluginName == "NO2_S5P_TROPOMI":
                pluginObj = NO2_S5P_TROPOMI(pluginInfo)
            elif pluginName == "SO2_S5P_TROPOMI":
                pluginObj = SO2_S5P_TROPOMI(pluginInfo)
            elif pluginName == "HAZE_H8_AHI":
                pluginObj = HAZE_H8_AHI(pluginInfo)
            elif pluginName == "DUST_H8_AHI":
                pluginObj = DUST_H8_AHI(pluginInfo)
            if pluginName == "AODDB_H8_AHI_COMPOSE":
                pluginObj = AODDB_H8_AHI_COMPOSE(pluginInfo)
            elif pluginName == "PM25_H8_AHI_COMPOSE":
                pluginObj = PM25_H8_AHI_COMPOSE(pluginInfo)
            elif pluginName == "PM10_H8_AHI_COMPOSE":
                pluginObj = PM10_H8_AHI_COMPOSE(pluginInfo)
            elif pluginName == "O3_S5P_TROPOMI_COMPOSE":
                pluginObj = O3_S5P_TROPOMI_COMPOSE(pluginInfo)
            elif pluginName == "NO2_S5P_TROPOMI_COMPOSE":
                pluginObj = NO2_S5P_TROPOMI_COMPOSE(pluginInfo)
            elif pluginName == "SO2_S5P_TROPOMI_COMPOSE":
                pluginObj = SO2_S5P_TROPOMI_COMPOSE(pluginInfo)

            return pluginObj
        except:
            return None
