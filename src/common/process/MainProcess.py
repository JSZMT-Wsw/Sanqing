# -- coding: utf-8 --

import datetime
import os

from src.common.config.CfgInputXml import CfgInputXml
from src.common.config.ConstParam import ConstParam
from src.common.utils.FileUtil import BaseFile
from src.common.utils.StringFormat import StringFormat


class MainProcess:
	"""程序入口类"""
	
	def __init__(self, cfgMgIns, pluginFactoryIns):
		"""cfgMgIns-配置管理器实例 pluginFactoryIns-算法插件工厂实例"""
		self.__cfgMgIns = cfgMgIns
		self.__pluginFactoryIns = pluginFactoryIns
		
		# 系统日志路径
		timeNow = datetime.datetime.now()
		self.__logPath = os.path.join(cfgMgIns.getLogFolder(),
		                              StringFormat.dateToStr(timeNow, "%Y%m%d", False) + ".log")
	
	def doProcess(self, args):
		if len(args) < 2:
			BaseFile.appendLogInfo(self.__logPath, BaseFile.LOGERROR, "未指定输入XML文件路径信息")
			return
		
		# 解析XML输入参数信息 获取产品算法标识
		cfgInputXml = CfgInputXml(args[1])
		cfgInputXml.loadCfgInfo(True, "xml", True)
		pluginName = cfgInputXml.getCfgInfoByKey(ConstParam.PLUGINNAME)
		if pluginName is None:
			BaseFile.appendLogInfo(self.__logPath, BaseFile.LOGERROR, "XML输入参数解析失败")
			return
		
		# 获取算法信息，getCfgInfoByKey(pluginName) 中返回的是一个 productInfo 类，在cfgProduct 重写了 getSecondRootXMLInfo 方法
		pluginInfo = self.__cfgMgIns.getProductCfg().getCfgInfoByKey(pluginName)
		if pluginInfo is None:
			BaseFile.appendLogInfo(self.__logPath, BaseFile.LOGERROR, "未检索到算法信息")
			return
		
		# 封装依赖项和输入参数信息 检测信息有效性
		pluginInfo.addAllInfoToDependMap(self.__cfgMgIns.getDependCfg().getCfgInfoMap())
		pluginInfo.addAllInfoToInputMap(cfgInputXml.getCfgInfoMap())
		if not (pluginInfo.isActive(self.__cfgMgIns)):
			BaseFile.appendLogInfo(self.__logPath, BaseFile.LOGERROR, "算法信息无效")
			return
		
		pluginObj = self.__pluginFactoryIns.getPlugin(pluginInfo)
		if pluginObj is None:
			BaseFile.appendLogInfo(self.__logPath, BaseFile.LOGERROR, "算法插件获取失败")
			return
		
		pluginObj.doProcess()
