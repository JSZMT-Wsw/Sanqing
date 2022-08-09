# -- coding: utf-8 -- 

import re
import time


class StringFormat:
    """字符串格式化工具类"""

    def __init__(self):
        pass

    @staticmethod
    def isEmpty(value):  
        """检测字符串是否为空"""
        try:
            if value is None or value.strip() == "":
                return True
            else:
                return False
        except:
            return True


    @staticmethod
    def isStrToNumber(value, isInt):  
        """字符串是否能转换为数值 整形/浮点型"""
        if StringFormat.isEmpty(value):
            return False        
        matchStr = "^(\\-|\\+)?\\d+$";
        if not isInt:
            matchStr = "^(\\-|\\+)?\\d+(\\.\\d+)?$";            
        return re.match(matchStr, value.strip()) and True or False
 
 
    @staticmethod
    def strToInt(value):
        """字符串转换为整形"""
        if not StringFormat.isStrToNumber(value, True):
            return None         
        return int(value)
        
        
    @staticmethod
    def strToFloat(value):    
        """字符串转换为浮点型"""
        if not StringFormat.isStrToNumber(value, False):
            return None         
        return float(value)
        
        
    @staticmethod
    def strToBoolean(value):   
        """字符串转换为布尔型"""
        if StringFormat.isEmpty(value):
            return False        
        value = value.lower()
        if value == "true":
            return True
        elif value == "false":
            return False
        else:
            return False 
        
        
    @staticmethod
    def getStrSplitArray(value, regex):        
        """分割字符串"""
        if StringFormat.isEmpty(value):
            return None         
        return value.split(regex)
        
        
    @staticmethod
    def isValidDateStr(value, fm):        
        """是否为有效的日期字符串 返回time.struct_time"""
        try:
            return time.strptime(value, fm) 
        except:
            return None
        
        
    @staticmethod
    def dateToStr(value, fm, isStruct):        
        """日期转换为字符串"""
        try: 
            if StringFormat.isEmpty(fm):
                fm = "%Y-%m-%d %H:%M:%S"                
            if isStruct:
                return time.strftime(fm, value)
            else:
                return value.strftime(fm)
        except:
            return None
    
    
    @staticmethod
    def dateToOracleStr(value, isStruct):        
        """日期转换为Oracle字符串"""
        oracleStr = StringFormat.dateToStr(value, "%Y-%m-%d %H:%M:%S", isStruct)        
        if not(oracleStr is None):
            oracleStr = "to_date(\'" + oracleStr + "\',\'YYYY-MM-DD HH24:MI:SS\')"
        return oracleStr
            
