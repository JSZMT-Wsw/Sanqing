# -- coding: utf-8 -- 

from src.common.jdbc.BaseDB import BaseDB
# import MySQLdb 
     
        
class DBMySQL(BaseDB):
    '''
    MySQL数据库操作类
    ''' 
            
    def __init__(self, dbInfo):
        BaseDB.__init__(self, dbInfo) 
    
    
    def openOwnConnect(self):
        try:  
            dbCon = MySQLdb.connect(self.dbInfo.getDBUrl(), self.dbInfo.getDBUser(), self.dbInfo.getDBPswd(), self.dbInfo.getDBName())
        except:
            pass
        finally:
            return dbCon