# -- coding: utf-8 --
  
import time
import subprocess  
    

class TimeoutError(Exception):
    """超时异常"""
    
    def __init__(self, err="cmd进程超时"):
        Exception.__init__(self, err)



class SysUtil:
    """系统工具类"""

    def __init__(self):
        pass

    @staticmethod
    def doCmd(cmdStr, timeOutSeconds=60 * 10):  
        """启动应用程序进程 默认超时时间10分钟"""
        p = subprocess.Popen(cmdStr, close_fds=True)  
        tBegin = time.time()
        secondsDelay = 0
        while True:
            if p.poll() is not None:
                break
            secondsDelay = time.time() - tBegin
            if secondsDelay > timeOutSeconds:
                p.kill()
                raise TimeoutError("cmd进程超时" + str(timeOutSeconds) + "s " + cmdStr)
            time.sleep(5)
