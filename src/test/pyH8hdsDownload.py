# -*- coding: utf-8 -*-
"""
@author: dyx
@time: 2021/4/15 16:25
@des:
"""
import os
import ftplib
import time
import re
import datetime


class myFTP:
    ftp = ftplib.FTP()

    # 链接ftp
    def __init__(self, host, port=21, YesdayNum=1):
        self.ftp.connect(host, port)
        self.__dayNum = YesdayNum

    # 登录FTP链接
    def Login(self, user, password):
        self.ftp.login(user, password)
        print(self.ftp.welcome)

    # 下载整个目录下的文件，LocalDir表示本地存储路径， emoteDir表示FTP路径
    def DownLoadFileTree(self, LocalDir, year, month, day, hour):
        LocalDir = LocalDir + "/" + year + "-" + month + "-" + day + "/" + hour
        if not os.path.exists(LocalDir):
            os.makedirs(LocalDir)

        RemoteDir = '/jma/hsd/' + year + month + '/' + day + '/' + hour
        # RemoteDir = '/jma/netcdf/' + year + month + '/' + day

        # 获取FTP路径下的全部文件名，以列表存储
        # 好像是乱序
        self.ftp.cwd(RemoteDir)
        RemoteNames = self.ftp.nlst()

        re_exp = 'HS_H08_' + year + month + day + '_' + hour + '00' + '_B[0-9]{2}' + '_FLDK_R[0-9]{2}_S0[1-5]10.DAT.bz2'
        # re_exp = 'NC_H08_' + year + month + day + '_0' + '[0-8]' + '00' + '_R21' + '_FLDK.06001_06001.nc'
        for file in RemoteNames:
            res = re.search(re_exp, file)
            if res:
                LocalFile = LocalDir + "/" + file
                RemoteFile = RemoteDir + "/" + file
                if not os.path.exists(LocalFile):
                    flag = self.DownLoadFile(LocalFile, RemoteFile)
                    if flag:
                        continue
                    else:
                        print(RemoteFile + 'get Field')
                        continue

    # 下载单个文件 LocalFile表示本地存储路径和文件名，RemoteFile是FTP路径和文件名
    def DownLoadFile(self, LocalFile, RemoteFile):
        bufSize = 102400

        file_handler = open(LocalFile, 'wb')
        print(file_handler)

        # 接收服务器上文件并写入本地文件
        self.ftp.retrbinary('RETR ' + RemoteFile, file_handler.write, bufSize)
        self.ftp.set_debuglevel(0)
        file_handler.close()

        return True


if __name__ == "__main__":
    host = 'ftp.ptree.jaxa.jp'
    user = 'wangshw_3clear.com'
    password = 'SP+wari8'

    LocalDir = 'D:\PUUSDATA\H8HSD'  # 根目录
    # LocalDir = 'D:\PUUSDATA\H8L1'  # 根目录

    # year = '2021'
    # month = '04'
    # day = '15'
    # hour = '00'
    obj = myFTP(host)
    obj.Login(user, password)

    start = '2021110100'
    end = '2021113000'
    date_format = "%Y%m%d%H"
    starttime = datetime.datetime.strptime(start, date_format)
    endtime = datetime.datetime.strptime(end, date_format)
    days = (endtime - starttime).days
    hours = 24*days
    for i in range(hours+1):
        delt = datetime.timedelta(hours=i)
        filetime = starttime + delt
        formattime = filetime.strftime(date_format)
        print(formattime)
        year = formattime[:4]
        month = formattime[4:6]
        day = formattime[6:8]
        hour = formattime[8:10]
        # print(year, month, day, hour)
        obj.DownLoadFileTree(LocalDir, year, month, day, hour)
