# -- coding: utf-8 --


class DBInfo:

    """数据库连接配置信息 类型/连接信息/用户/密码/库名（MySQL用）"""
           
    def __init__(self, dbType, dbUrl, dbUser, dbPswd, dbName): 
        self.__dbType = dbType
        self.__dbUrl = dbUrl
        self.__dbUser = dbUser
        self.__dbPswd = dbPswd 
        self.__dbName = dbName 
        
        
    def getDBType(self): 
        return self.__dbType 
     
    def getDBUrl(self): 
        return self.__dbUrl   
    
    def getDBUser(self): 
        return self.__dbUser 
    
    def getDBPswd(self): 
        return self.__dbPswd
    
    def getDBName(self): 
        return self.__dbName
     
        
