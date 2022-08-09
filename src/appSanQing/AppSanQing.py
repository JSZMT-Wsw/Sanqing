# -- coding: utf-8 -- 
# 注意：cartopy、gdal、geopandas等公用shapely包，
# 此处有严格的顺序，必须先导入cartopy/geopandas，再导入gdal即可，否则会报错：
#    File "shapely\speedups\_speedups.pyx", line 408, in shapely.speedups._speedups.geos_linearring_from_py
# ValueError: GEOSGeom_createLinearRing_r returned a NULL pointer
import cartopy.crs as ccrs  # 由于后续有gdal导入，因此必须先导入cartopy包
import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
projDir = os.path.split(rootPath)[0]
sys.path.append(projDir)

from src.common.config.MgCfg import MgCfg
from src.common.process.MainProcess import MainProcess
from src.appSanQing.pluginsSanQing.PluginFactorySanQing import PluginFactorySQ

projDir = os.path.split(rootPath)[0]

if __name__ == '__main__':
    cfgMgIns = MgCfg(projDir)
    cfgMgIns.loadCfgInfo()
    appMain = MainProcess(cfgMgIns, PluginFactorySQ())
    appMain.doProcess(sys.argv)
