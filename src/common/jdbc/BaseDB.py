# -- coding: utf-8 --  
    
class BaseDB():
    '''
    数据库操作基类
    ''' 
            
    def __init__(self, dbInfo):
        self.dbInfo = dbInfo
    
    
    def getDBType(self):
        '''
        获取当前数据库类型 字符串
        '''
        dbType = None        
        try:
            dbType = self.dbInfo.getDBType()
        except:
            pass
        return dbType
    
    
    def queryInfo(self, sqlStr):
        '''
        信息查询
        '''
        result = None        
        try:
            dbCon = self.__openConnect()
            if dbCon != None:
                cursor = dbCon.cursor()
                cursor.execute(sqlStr)
                result = cursor.fetchall()
                cursor.close()
        except:
            pass
        finally:
            self.__closeConnect(dbCon)
        return result
    
    
    def updateInfo(self, sqlStr):
        '''
        信息增删改
        '''
        flag = False        
        try:
            dbCon = self.__openConnect()
            if(dbCon != None):
                cursor = dbCon.cursor()
                cursor.execute(sqlStr)
                dbCon.commit()
                cursor.close()
                flag = True
        except:
            pass
        finally:
            self.__closeConnect(dbCon)
        return flag
    
    
    def openOwnConnect(self):
        '''
        待具体实现的子类覆盖
        '''    
        return None
    
    def __openConnect(self):
        '''
        打开连接
        '''    
        if(self.dbInfo == None):
            return None
        return self.openOwnConnect()    
         
         
    def __closeConnect(self, dbCon):
        '''
        关闭连接
        '''
        if(dbCon != None):
            try:
                dbCon.close()
            except:
                pass
  
    
    def testConnect(self):
        '''
        连接测试
        '''
        flag = False        
        try:
            dbCon = self.__openConnect()
            if(dbCon != None):
                flag = True
        except:
            pass
        finally:
            self.__closeConnect(dbCon)
        return flag
    
    