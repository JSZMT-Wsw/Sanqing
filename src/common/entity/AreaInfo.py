# -- coding: utf-8 --


class AreaInfo:
	"""行政区划信息 递归结构 id/name/所属id/下辖行政区划字典（id+行政区划对象）"""
	
	def __init__(self, areaID, areaName, level, dircID):
		self.__areaID = areaID
		self.__areaName = areaName
		self.__level = level
		self.__dircID = dircID
		self.__areaMap = {}
	
	def addArea(self, areaInfo):
		"""添加行政区划 id已存在或所属id不匹配不添加"""
		
		if areaInfo is None:
			return
		areaID = areaInfo.getAreaID()
		dircID = areaInfo.getDircID()
		if dircID != self.__areaID:
			return
		if areaID in self.__areaMap.keys():
			return
		self.__areaMap[areaID] = areaInfo
	
	def getAreaID(self):
		return self.__areaID
	
	def getAreaName(self):
		return self.__areaName
	
	def getLevel(self):
		return self.__level
	
	def getDircID(self):
		return self.__dircID
	
	def getAreaMap(self):
		return self.__areaMap
	
	def isContainsID(self, areaID):
		"""是否包含直辖的指定id行政区划信息"""
		if areaID in self.__areaMap.keys():
			return True
		return False
	
	def isSubChildID(self, childID, childLevel):
		"""指定ID号是否隶属于当前行政区划或当前行政区划"""
		flagChild = False
		
		if self.__level == childLevel:
			if childID == self.__areaID:
				flagChild = True
		else:
			if self.__level == 0:
				flagChild = True
			elif self.__level == 1:  # 当前行政区划为省
				if childLevel == 2 and self.isContainsID(childID):
					flagChild = True
				elif childLevel == 3:
					areaCounty = self.getAreaByID(childID)
					if not (areaCounty is None):
						areaCity = self.getAreaByID(areaCounty.getDircID())
						if not (areaCity is None) and self.isContainsID(areaCity.getAreaID()):
							flagChild = True
			elif self.__level == 2:  # 当前行政区划为市
				if childLevel == 3:
					if self.isContainsID(childID):
						flagChild = True
		
		return flagChild
	
	def getAreaIDList(self):
		"""获取直辖的行政区划id列表"""
		ary = []
		for key in self.__areaMap.keys():
			ary.append(key)
		if len(ary) == 0:
			return None
		else:
			return ary
	
	def getAreaByID(self, areaID):
		"""递归查询指定id行政区划对象"""
		return self.__getArea(areaID, self)
	
	def __getArea(self, areaID, areaInfo):
		areaMap = areaInfo.getAreaMap()
		if len(areaMap) == 0:
			return None
		if areaID in areaMap.keys():
			return areaMap[areaID]
		areaInfoCur = None
		for key in areaMap.keys():
			areaInfoCur = self.__getArea(areaID, areaMap[key])
			if not (areaInfoCur is None):
				break
		return areaInfoCur
	