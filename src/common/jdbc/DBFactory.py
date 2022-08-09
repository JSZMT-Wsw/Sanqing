# -- coding: utf-8 -- 

from src.common.jdbc.DBOracle import DBOracle
from src.common.jdbc.DBMySQL import DBMySQL


class DBFactory():
    '''
    数据库工具工厂
    ''' 
  
    __instance = None
    
    
    def __init__(self):
        self.__dbObj = None
        self.__dbInfo = None
        
       
    @staticmethod
    def getInstance():
        if DBFactory.__instance == None:
            DBFactory.__instance = DBFactory() 
        return DBFactory.__instance
        
        
    def setDBInfo(self, dbInfo):
        # getDBObj()之前设置
        self.__dbInfo = dbInfo
        
        
    def getDBObj(self):
        '''
        获取当前数据库操作实例
        '''
        try:
            if self.__dbObj == None and self.__dbInfo != None:
                dbType = self.__dbInfo.getDBType().lower() 
                if dbType == "oracle":
                    self.__dbObj = DBOracle(self.__dbInfo)
                elif dbType == "mysql":
                    self.__dbObj = DBMySQL(self.__dbInfo)
                else:
                    pass 
            return self.__dbObj
        except:
            return None

      


           
      
            

        
