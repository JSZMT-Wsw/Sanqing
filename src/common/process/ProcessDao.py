# -- coding: utf-8 -- 
 
from common.utils.StringFormat import StringFormat
 
class ProcessDao():
    '''
   数据库操作对象基类
    '''  
    
    def __init__(self, dbObj, cfgMgIns): 
        '''dbObj-数据库实例 cfgMgIns-配置管理器实例''' 
        self.dbObj = dbObj
        self.dbType = dbObj.getDBType()
        self.cfgMgIns = cfgMgIns
        
    
    def isExist(self, sqlStr):
        '''
        查询指定信息是否存在
        ''' 
        if self.dbObj == None or StringFormat.isEmpty(sqlStr):
            return False        
        result = self.dbObj.queryInfo(sqlStr)        
        if result != None and len(result) > 0:
            return True
        else:
            return False
        
        
    def upDateProdInfo(self, tableName, filedMap={}):
        '''
        更新信息 子
        ''' 
        return False
     
    
    
    def deleteProdInfo(self, tableName, filedMap={}): 
        '''
        删除信息
        '''  
        return False
        
                
            
     
    
