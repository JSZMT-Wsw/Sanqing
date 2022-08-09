# encoding: utf-8
"""
@author: DYX
@file: MapPy.py
@time: 2020/10/14 11:51
@desc:
"""

from src.common.CartopyMapPy.Layout.Process.MainProcess import MainProcess
from src.common.CartopyMapPy.Layout.config.MgCfg import MgCfg


def MapPy(tifFile, lyrFile, rgbPseudo, staMap, shpMark, shpFile, outDir, plugainName, issueLabelText, Colors, ColorLevels, ColorLabels,
          templatePath):
    """
    出图函数
    :param tifFile: 待渲染的tif路径
    :param lyrFile: dict={}  专题图叠加其他数据信息
    :param rgbPseudo dict={} 专题图叠加RGB三通道数据信息
    :param staMap: 与tif相交的ID编码，dict={}
    :param shpMark: 矢量标识 County、City、Province、Nation
    :param shpFile: 矢量路径
    :param outDir:  当前输出文件路径
    :param plugainName: 插件名
    :param issueLabelText: 时间期次
    :param Colors: 颜色列表 list=[]
    :param ColorLevels: 颜色表刻度 list=[v1, v2, ...vn]比颜色表多1
    :param ColorLabels: 颜色表标签
    :param templatePath: 模板路径
    :return:
    """
    cfg = MgCfg(plugainName, templatePath)
    cfg.loadCfgInfo()
    map = MainProcess(cfg, tifFile, lyrFile, rgbPseudo, staMap, shpMark, shpFile, outDir, issueLabelText, Colors, ColorLevels, ColorLabels)
    returnMapPath = map.doProcess()

    return returnMapPath
