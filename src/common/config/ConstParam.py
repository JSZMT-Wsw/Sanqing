# -- coding: utf-8 --


class ConstParam:
	"""常量信息"""
	
	def __init__(self):
		pass
	
	# --------- properties字段信息 ---------
	# 系统依赖文件目录
	DEPENDFOLDER = "DependFolder"
	
	# 算法目录
	IDLAPPFOLDER = "IDLAppFolder"
	
	# 算法执行临时目录
	TEMPFOLDER = "TempFolder"
	
	# 行政区划顶级ID编号
	TOPAREAID = "TopAreaID"
	
	# 产品任务主表
	PRODTABLENAME = "ProductTableName"
	
	# 数据库类型
	DBTYPE = "DBType"
	
	# 数据库连接字符串信息
	DBURL = "DBUrl"
	
	# 数据库用户名称
	DBUser = "DBUser"
	
	# 数据库密码
	DBPswd = "DBPswd"
	
	# 数据库名称
	DBName = "DBName"
	
	# IDLExe路径
	IDLEXEPATH = "IDLExePath"
	
	# 镶嵌数据集目录
	MOSAICFOLDER = "MosaicFolder"
	
	# 镶嵌数据集GDB路径
	GDBPATH = "GDBPath"
	
	# Geoserver存放一级类目录
	GEOSERVERFolder = "GeoserverFolder"
	
	# --------- properties字段信息 ---------
	# ----------- 产品算法标识信息 -----------
	ProductMarkMap = {}
	# 产品算法信息字典 算法名称+算法信息
	
	PLUGINNAME = "PluginName"
	# 算法名称
	
	PRODDESP = "ProdDesp"
	# 算法描述信息
	
	FILEFILTER = "Filter"
	# 文件过滤正则
	
	REMAP = "ReMaps"
	# 重分类
	
	OUTTIMEMIN = "OutTimeMin"
	# 超时时间-分钟
	
	FILLVALUE = "FillValue"
	# 无效值
	
	TYPE = "Type"
	# 分级标准类型
	
	AREAID = "areaID"
	# 行政区划ID
	
	ISSUE = "issue"
	# 期号
	
	CYCLE = "cycle"
	# 周期
	
	INPUTFILE = "inputFile"
	# 输出目录
	
	OUTFOLDER = "outFolder"
	# 输出目录
	
	OUTXMLPATH = "outXMLPath"
	# xml输出路径
	
	OUTLOGPATH = "outLogPath"
	# 日志输出路径
	
	MINOUTTIME = 10
	# 最小超时时间-10分钟
	
	MAXOUTTIME = 120
	# 最大超时时间-120分钟
	# ----------- 产品算法标识信息 -----------
	
	# ---------- 算法执行过程常量信息 ----------
	STATESUCESS = "1"
	# 成功标识
	
	STATEFAILED = "2"
	# 失败标识
	# --------- 算法执行过程常量信息 ----------
	
	# --------- 统计执行类型常量信息 ----------
	GRADATIONSTATISTICS = "1"  # 分级统计
	NORMALSTATISTICS = "2"  # 正常统计
	ALLSTATISTICS = "3"  # 正常统计 + 分级统计
