# -- coding: utf-8 -- 

from src.common.jdbc.BaseDB import BaseDB
import cx_Oracle 
     
        
class DBOracle(BaseDB):
    '''
    Oracle数据库操作类
    ''' 
            
    def __init__(self, dbInfo):
        BaseDB.__init__(self, dbInfo) 
    
    
    def openOwnConnect(self):
        try:  
            dbCon = cx_Oracle.connect(self.dbInfo.getDBUrl())
        except:
            pass
        finally:
            return dbCon