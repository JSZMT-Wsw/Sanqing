# -*- coding: utf-8 -*-
'''
@File  : PM25_H8_AHI.py
@Author: admin#
@Date  : 2020/11/19 17:59
@Desc  : 
'''

import warnings

warnings.filterwarnings("ignore")
import time
import joblib  # python3 无需从sklearn中导入
import netCDF4 as nc
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from osgeo import osr
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import mean_squared_error, explained_variance_score, mean_absolute_error
from src.common.utils.GeoProcessUtil import GeoProcessUtil


def get_sample_data(ARPFiles, STNFiles, QXFiles, aod_features, stn_features, qx_features):
    # 文件个数检查
    if len(ARPFiles) == len(STNFiles) == len(QXFiles):
        print(("train file aod-stn-qx nums is match, OK!"))
    else:
        print("train file aod-stn-qx nums is not match")
        return

    # 文件排序
    ARPFiles.sort()
    STNFiles.sort()
    QXFiles.sort()

    df = []
    for each_file_idx in range(len(ARPFiles)):
        # 文件时间匹配
        arp_file_path = ARPFiles[each_file_idx]
        if os.path.exists(arp_file_path) == False:
            continue

        stn_file_path = STNFiles[each_file_idx]
        if os.path.exists(stn_file_path) == False:
            continue

        qx_file_path = QXFiles[each_file_idx]
        if os.path.exists(qx_file_path) == False:
            continue

        time_flag = file_time_match(arp_file_path, qx_file_path, stn_file_path)
        if not (time_flag) == True:
            return

        # 以环境站为主，空间站点匹配
        """
        注意pandas用法：
        、、usecols: []   按列索引(标签)取数据，但是读取的数据顺序仍然按csv文件中的顺序，不以usecols中指定的列顺序读出
            若要以usecols中指定顺序，则   pd.read_csv(file, usecols=list)[list].values
        、、encoding:存在中文字符   encoding='gb18030'
        、、df.loc: 按标签选择数据   df.loc[:, col1:col2]
        、、df.iloc：按索引选择数据  df.iloc[row1:row2, col1:col2]
        、、df.index = []  更改df的行索引
        、、df._stat_axis.values.tolist()  行名称
        、、df.columns.values.tolist()  列名称
        、、pd.concat([df1, df2], axis=0/1) axis=0续行,   axis=1续列
        """
        pos_usecols = ['LONGITUDE', 'LATITUDE']
        stn_pos = pd.read_csv(stn_file_path, usecols=pos_usecols, encoding='gb18030')[pos_usecols].values  # 环境站经纬度
        stn_lon = stn_pos[:, 0]
        stn_lat = stn_pos[:, 1]
        qx_pos = pd.read_csv(qx_file_path, usecols=pos_usecols, encoding='gb18030')[pos_usecols].values  # 气象站经纬度
        qx_lon = qx_pos[:, 0]
        qx_lat = qx_pos[:, 1]

        flg = []  # 获取每个环境站对应的最近的气象站的行索引
        for idx in range(len(stn_lon)):
            diff = pow((qx_lon - stn_lon[idx]), 2) + pow((qx_lat - stn_lat[idx]), 2)
            dif_min = np.argmin(diff)
            flg.append(dif_min)

        # 重新构造新的df，以 环境站要素+qx_features+aod
        src_df = pd.read_csv(stn_file_path, encoding='gb18030')  # 环境站df

        df_append = pd.read_csv(qx_file_path, usecols=qx_features, encoding='gb18030')[qx_features]
        df_append = df_append.iloc[flg, :]  # 每个环境站所对应的气象站的要素df
        df_append.index = src_df._stat_axis.values.tolist()  # 修改行索引和环境站索引一直

        dst_df = pd.concat([src_df, df_append], axis=1)

        # 添加aod列
        # 添加aod列
        AOD, XSize, YSize, geotransform = read_H8_ncfile(arp_file_path)
        # 深蓝算法反演AOD
        # AOD, XSize, YSize, geotransform = GeoProcessUtil.read_tiff(arp_file_path, 1)

        AOD[AOD < 0] = np.nan

        aod = read_aod_mean(AOD, geotransform, stn_lon, stn_lat)
        dst_df['AOD'] = aod

        df.append(dst_df)

    # 行过滤
    out_df = pd.concat(df, axis=0)
    for feature in stn_features + qx_features + aod_features:
        out_df = out_df.loc[lambda x: x[feature] > 0]

    print("train df is get, OK!")
    return out_df


def rf_model_fit(df, qx_features, aod_features, stn_features, model_file, model_plot, model_scatter):
    """模型训练"""
    x_data = df.loc[:, qx_features + aod_features]
    y_data = df.loc[:, stn_features]

    # 划分训练集和验证集
    """
    random_state就是为了保证程序每次运行都分割一样的训练集合测试集。否则，同样的算法模型在不同的训练集和测试集上的效果不一样
    """
    X_train, X_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.3, random_state=0)

    criterion = ['mse', 'mae']
    n_estimators = [int(x) for x in np.linspace(start=200, stop=2000, num=10)]  #
    max_features = ['auto', 'sqrt']
    max_depth = [int(x) for x in np.linspace(10, 100, num=10)]
    max_depth.append(None)  # 加默认值
    min_samples_split = [2, 5, 10]
    min_samples_leaf = [1, 2, 4]
    bootstrap = [True, False]
    random_grid = {'criterion': criterion,
                   'n_estimators': n_estimators,
                   'max_features': max_features,
                   'max_depth': max_depth,
                   'min_samples_split': min_samples_split,
                   'min_samples_leaf': min_samples_leaf,
                   'bootstrap': bootstrap}
    clf = RandomForestRegressor()
    clf_random = RandomizedSearchCV(estimator=clf, param_distributions=random_grid,
                                    n_iter=10, cv=3, verbose=2, random_state=42, n_jobs=1, iid=False)
    clf_random.fit(X_train, y_train)
    BP = clf_random.best_params_
    print(clf_random.best_params_)

    rf = RandomForestRegressor(criterion=BP['criterion'], bootstrap=BP['bootstrap'], max_features=BP['max_features'],
                               max_depth=BP['max_depth'], min_samples_split=BP['min_samples_split'],
                               n_estimators=BP['n_estimators'], min_samples_leaf=BP['min_samples_leaf'])
    rf.fit(X_train, y_train)
    y_train_pred = rf.predict(X_train)
    y_test_pred = rf.predict(X_test)

    # 测试各输入因子的重要性
    print("各输入因子的重要性：")
    print(rf.feature_importances_)

    # 模型评价
    print("决策树模型评估--训练集：")
    print('训练R^2：%s' % rf.score(X_train, y_train))
    print('均方差：%s' % mean_squared_error(y_train, y_train_pred))
    print('绝对差：%s' % mean_absolute_error(y_train, y_train_pred))
    print('解释度：%s' % explained_variance_score(y_train, y_train_pred))

    print("决策树模型评估--验证集：")
    print('验证R^2:%s' % rf.score(X_test, y_test))
    print('均方差：%s' % mean_squared_error(y_test, y_test_pred))
    print('绝对差：%s' % mean_absolute_error(y_test, y_test_pred))
    print('解释度：%s' % explained_variance_score(y_test, y_test_pred))

    R2 = rf.score(X_test, y_test)
    X_True = y_test.iloc[:, 0].values
    Y_Pred = y_test_pred
    rf_model_accuracy_plot(X_True, Y_Pred, R2, model_plot)
    rf_model_accuracy_scatter(X_True, Y_Pred, model_scatter)

    # 模型参数存储
    joblib.dump(rf, model_file)


def rf_model_predict(issue, model_file_path, shpFile, curARPFile, curQXFile, qx_features, tempFolder, fillValue):
    rf = joblib.load(model_file_path)  # 调用

    # 文件检测
    if os.path.exists(curARPFile) == False or os.path.exists(curQXFile) == False:
        print("pred file is not exists, Faild")
        return
    print("pred file is exists, OK!")

    # 时间匹配
    qx_file_name = os.path.basename(curQXFile)
    qx_file_time = os.path.splitext(qx_file_name)[0]
    if qx_file_time != issue[0:10]:
        print("pred file aod-qx time is match, Faild!")
        return
    print("pred file aod-qx time is match, OK!")

    # 读取AOD栅格数据，并获取裁剪后的XSize, YSize
    AOD, XSize, YSize, geotransform = read_H8_ncfile(curARPFile)
    AOD[AOD < 0] = fillValue
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)
    ds = GeoProcessUtil.write_tiff(AOD, XSize, YSize, 1, geotransform, sr.ExportToWkt(), out_path=None,
                                   no_data_value=fillValue)
    aod_clip_file = tempFolder + "/" + "aod_clip_file.tif"
    GeoProcessUtil.clip_by_shp(ds, shpFile, out_raster_file=aod_clip_file)
    aod, XSize, YSize, geotrans, proj = GeoProcessUtil.read_tiff(aod_clip_file, 1)

    # 获取训练数据
    x_arry = []
    for z_field in qx_features:
        z_field_file = GeoProcessUtil.interpolation_by_points(curQXFile, z_field, shpFile,
                                                              tempFolder, tempFolder + '/' + z_field + '.tif',
                                                              cellsize=0.05, interpolation_type="invdist")
        z_field_data = GeoProcessUtil.read_tiff(z_field_file, 1, buf_xsize=XSize, buf_ysize=YSize)[0]
        x_arry.append(z_field_data)
    x_arry.append(aod)
    print("pred data is get, OK!")

    # 使用rf模型预测
    x_arry = np.array(x_arry)
    dim = x_arry.shape
    x_pred = x_arry.reshape(dim[0], dim[1] * dim[2])
    x_pred = np.transpose(x_pred)

    y_pred = rf.predict(x_pred)

    # pm25 行转数组
    pm25 = y_pred.reshape(dim[1], dim[2])
    pm25[aod < 0] = fillValue
    pm25[pm25 > 200] = 200

    print("pred PM25 Finish, OK!")

    return pm25, XSize, YSize, geotrans, proj


def file_time_match(ARPFile, QXFile, STNFile=None):
    """
    文件时间匹配   本次以ARP(utc)、STN、QX三个文件
    可能存在环境站不需要的情况，比如拿到模型开始预测
    、、时间匹配需要针对性改动
    """

    arp_file_name = os.path.basename(ARPFile)
    arp_file_time = "".join(arp_file_name.split("_")[1:3])[0:10]

    timestp = datetime.strptime(arp_file_time, "%Y%m%d%H") + timedelta(hours=8)
    # timestp = datetime.strptime(arp_file_time, "%Y%m%d%H")
    arp_file_time_bj = timestp.strftime("%Y%m%d%H")

    qx_file_name = os.path.basename(QXFile)
    qx_file_time = os.path.splitext(qx_file_name)[0]

    if STNFile is None:
        stn_file_time = arp_file_time_bj
    else:
        stn_file_name = os.path.basename(STNFile)
        stn_file_time = os.path.splitext(stn_file_name)[0]

    if arp_file_time_bj == stn_file_time and arp_file_time_bj == qx_file_time:
        print("train curfile time is match, OK!")
        return True

    else:
        print("train curfile is not match, False!")
        return False


def read_H8_ncfile(h8_nc_file):
    """读取H8 nc文件"""
    nc_data_obj = nc.Dataset(h8_nc_file)
    Lon = nc_data_obj.variables["longitude"][:]
    Lat = nc_data_obj.variables["latitude"][:]
    AOD_arr = np.asarray(nc_data_obj.variables["AOT_L2_Mean"])  # 将AOD数据读取为数组
    AOD = np.array([AOD_arr])[0]
    nc_data_obj.close()

    YSize = len(Lat)
    XSize = len(Lon)
    LonMin, LatMax, LonMax, LatMin = [Lon.min(), Lat.max(), Lon.max(), Lat.min()]
    Lon_Res = (LonMax - LonMin) / (float(XSize) - 1)
    Lat_Res = (LatMax - LatMin) / (float(YSize) - 1)
    geotransform = (LonMin, Lon_Res, 0, LatMax, 0, -Lat_Res)

    return AOD, XSize, YSize, geotransform


def read_aod_mean(arry, geotransform, stn_lon, stn_lat):
    """取栅格环境站中心点 n×n窗口内均值"""

    aod = []
    points = list(zip(stn_lon, stn_lat))
    for point in points:
        lon = point[0]
        lat = point[1]
        ptidx = geo2imagexy(geotransform, lon, lat)
        row = int(ptidx[1])
        col = int(ptidx[0])

        if row < 2 and col < 2:
            winData = arry[row, col]
        else:
            winData = arry[row - 2: row + 3, col - 2: col + 3]
        aodmean = np.nanmean(winData)
        if np.isnan(aodmean):   aodmean = -999.0
        aod.append(aodmean)

    return aod


def geo2imagexy(trans, x, y):
    '''
    根据GDAL的六 参数模型将给定的投影或地理坐标转为影像图上坐标（行列号）
    :param trans: GDAL地理数据仿射矩阵
    :param x: 投影或地理坐标x
    :param y: 投影或地理坐标y
    :return: 影坐标或地理坐标(x, y)对应的影像图上行列号(row, col)
    '''
    a = np.array([[trans[1], trans[2]], [trans[4], trans[5]]])
    b = np.array([x - trans[0], y - trans[3]])
    return np.linalg.solve(a, b)  # 使用numpy的linalg.solve进行二元一次方程的求解


def rf_model_accuracy_plot(X_True, Y_Pred, R2, plot_path):
    # 折线图
    fig, ax = plt.subplots(figsize=(12, 8))

    dim = Y_Pred.shape
    ax.plot(range(dim[0]), Y_Pred, '-^', linewidth=1)
    ax.plot(range(dim[0]), X_True, '--v', linewidth=1)

    ax.text(0.1, 0.92, 'R$\mathregular{^2}$=' + str(round(R2, 2)), size=12, transform=ax.transAxes)
    ax.legend(['Simulation_PM2.5', 'Station_PM2.5'])
    fig.savefig(plot_path, bbox_inches='tight')


def rf_model_accuracy_scatter(X_True, Y_Pred, scatter_path):
    """散点图"""
    fig = plt.figure(figsize=[10, 10])
    deg = 1
    parameter = np.polyfit(X_True, Y_Pred, deg)  # 拟合deg次多项式
    p = np.poly1d(parameter)  # 拟合deg次多项式
    RMSE = np.sqrt(metrics.mean_squared_error(X_True, Y_Pred))
    aa = ''  # 方程拼接  ——————————————————
    for i in range(deg + 1):
        bb = round(parameter[i], 2)
        if bb > 0:
            if i == 0:
                bb = str(bb)
            else:
                bb = '+' + str(bb)
        else:
            bb = str(bb)
        if deg == i:
            aa = aa + bb
        else:
            aa = aa + bb + 'X'  # 方程拼接  ——————————————————
    aa = 'y=' + aa
    plt.scatter(X_True, Y_Pred, s=15)  # 原始数据散点图
    plt.plot(X_True, p(X_True), color='g')  # 画拟合曲线
    plt.plot([0, 100], [0, 100], color='black', linewidth=0.5, linestyle='--')
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.text(5, 90, aa, size=12)
    plt.text(5, 87, 'R$\mathregular{^2}$:' + str(round(np.corrcoef(Y_Pred, p(X_True))[0, 1] ** 2, 2)), size=12)
    plt.text(5, 84, "RMSE=" + str("%.2f" % RMSE), size=12)
    plt.xlabel("Station_PM2.5", fontname='Times New Roman', size=12)
    plt.ylabel('RF_PM2.5', fontname='Times New Roman', size=12)

    fig.savefig(scatter_path, bbox_inches='tight')


def rf_pred_accuracy_scatter(issue, pm_arry, geotrans, curSTNFile, stn_features, scatter_path):
    """
    rf模型预测结果与真实结果比较
    、、该模型是后比对模型
    """
    # 文件时间匹配
    if os.path.exists(curSTNFile) == False:
        return
    stn_file_name = os.path.basename(curSTNFile)
    stn_file_time = os.path.splitext(stn_file_name)[0]
    if stn_file_time != issue[0:10]:
        return

    uscols_list = ['LONGITUDE', 'LATITUDE'] + stn_features
    stn_pm = pd.read_csv(curSTNFile, usecols=uscols_list, encoding='gb18030')[uscols_list].values  # 环境站经纬度+PM

    pm_arry[pm_arry < 0] = np.nan

    pm_true = []
    pm_pred = []
    for point in stn_pm:

        if point[2] < 0:  # 站点PM为无效值，剔除该点
            continue

        ptidx = geo2imagexy(geotrans, point[0], point[1])
        row = int(ptidx[1])
        col = int(ptidx[0])

        if row < 2 and col < 2:
            winData = pm_arry[row, col]
        else:
            winData = pm_arry[row - 2: row + 3, col - 2: col + 3]
        pmmean = np.nanmean(winData)

        if np.isnan(pmmean):  # 模型计算出的PM窗口均值为无效值，剔除
            continue

        pm_pred.append(pmmean)
        pm_true.append(point[2])

    rf_model_accuracy_scatter(pm_true, pm_pred, scatter_path)
