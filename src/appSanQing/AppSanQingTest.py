# -- coding: utf-8 --

# 注意：cartopy、gdal、geopandas等公用shapely包，
# 此处有严格的顺序，必须先导入cartopy/geopandas，再导入gdal即可，否则会报错：
#    File "shapely\speedups\_speedups.pyx", line 408, in shapely.speedups._speedups.geos_linearring_from_py
# ValueError: GEOSGeom_createLinearRing_r returned a NULL pointer
import cartopy.crs as ccrs  # 由于后续有gdal导入，因此必须先导入cartopy包
import datetime
import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
projDir = os.path.split(rootPath)[0]
sys.path.append(projDir)

from src.common.config.MgCfg import MgCfg
from src.common.process.MainProcess import MainProcess
from src.common.utils.StringFormat import StringFormat
from src.appSanQing.pluginsSanQing.PluginFactorySanQing import PluginFactorySQ

projDir = os.path.split(rootPath)[0]

# 大气
argsAODDB_H8_AHI = ["test", "D:/001Project/006SanQing/RSPlatForm/XMLDemo/InputAODDB_H8_AHI.xml"]
argsAOD_H8_AHI = ["test", "D:/001Project/006SanQing/RSPlatForm/XMLDemo/InputAOD_H8_AHI.xml"]
argsPM25_H8_AHI = ["test", "D:/001Project/006SanQing/RSPlatForm/XMLDemo/InputPM25_H8_AHI.xml"]
argsPM10_H8_AHI = ["test", "D:/001Project/006SanQing/RSPlatForm/XMLDemo/InputPM10_H8_AHI.xml"]
argsDUST_SATPY_H8_AHI = ["test", "D:/001Project/006SanQing/RSPlatForm/XMLDemo/InputDUST_SATPY_H8_AHI.xml"]
argsNO2_S5P_TROPOMI = ["test", "D:/001Project/006SanQing/RSPlatForm/XMLDemo/InputNO2_S5P_TROPOMI_new.xml"]
argsSO2_S5P_TROPOMI = ["test", "D:/001Project/006SanQing/RSPlatForm/XMLDemo/InputSO2_S5P_TROPOMI.xml"]
argsO3_S5P_TROPOMI = ["test", "D:/001Project/006SanQing/RSPlatForm/XMLDemo/InputO3_S5P_TROPOMI.xml"]
argsDUST_H8_AHI = ["test", "D:/001Project/006SanQing/RSPlatForm/XMLDemo/dust_test/InputDUST_202103151300.xml"]
argsCH4_S5P_TROPOMI = ["test", "D:/001project/003WeiFang/RSPlatForm/XMLDemo/InputCH4_S5P_TROPOMI.xml"]
argsPM25_H8_AHI_COMPOSE = ["test", "D:/001Project/006SanQing/RSPlatForm/XMLDemo/InputPM25_H8_AHI_COMPOSE.xml"]
argsSO2_S5P_TROPOMI_COMPOSE = ["test", "D:/001Project/006SanQing/RSPlatForm/XMLDemo/InputSO2_S5P_TROPOMI_COMPOSE.xml"]
argstest = ["test", "D:/001Project/006SanQing/RSPlatForm/XMLDemo/InputHAZE_H8_AHI.xml"]

dateStr = StringFormat.dateToStr(datetime.datetime.now(), "", False)
print("Start Time:", dateStr)
print("--------------------------------------")

if __name__ == '__main__':
    # xml_floder = r'D:/001Project/006SanQing/RSPlatForm/XMLDemo/dust_test'
    # xml_list = os.listdir(xml_floder)
    # for i in xml_list:
    #     xml_path = xml_floder + "//" + i
    #     cfgMgIns = MgCfg(projDir)
    #     cfgMgIns.loadCfgInfo()
    #     appMain = MainProcess(cfgMgIns, PluginFactorySQ())
    #     appMain.doProcess(['test', xml_path])
    cfgMgIns = MgCfg(projDir)
    cfgMgIns.loadCfgInfo()
    appMain = MainProcess(cfgMgIns, PluginFactorySQ())
    appMain.doProcess(argstest)

print("--------------------------------------")
dateStr = StringFormat.dateToStr(datetime.datetime.now(), "", False)
print("End  Time:", dateStr)
