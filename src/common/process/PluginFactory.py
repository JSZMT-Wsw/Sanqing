# -- coding: utf-8 --

class PluginFactory():
    """产品算法插件工厂基类 具体应用从本类继承（仅起到约束作用）实现getPlugin()方法"""
    
    def __init__(self): 
        self.name = "PluginFactory"
    
    
    def getPlugin(self, pluginInfo):
        """获取算法对象 pluginInfo-产品算法信息"""
        return None

    
    
    
            
