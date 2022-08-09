# -- coding: utf-8 --

from src.common.process.ProcessBase import BaseProcess
from src.common.utils.FileUtil import BaseFile
from satpy import Scene, find_files_and_readers
from pyresample import create_area_def
import datetime

class DUST_SATPY_H8_AHI(BaseProcess):
    '''
    使用satpy出图沙尘
    '''

    def __init__(self, pluginParam):
        BaseProcess.__init__(self, pluginParam)
        self.isOutExe = False
        self.processType = 1

    def doInnerPy(self):
        try:
            self.processType == 1
            BaseFile.appendLogInfo(self.logPath, "1%", "开始进行算法处理...")
            # xml中的input
            inputFloder = self.pluginParam.getInputFile()
            if inputFloder is None or BaseFile.isFileOrDir(inputFloder) != BaseFile.ISDIR:
                print("输入文件不存在")
                return None
            composite = 'dust'
            res = 0.01
            self.pluginParam.getCurAreaInfo
            area_extent = (73, 12, 136, 56)
            # area_extent = (self.outExtentMap[self.pluginParam.getAreaID()]['xmin'],
            #                self.outExtentMap[self.pluginParam.getAreaID()]['ymin'],
            #                self.outExtentMap[self.pluginParam.getAreaID()]['xmax'],
            #                self.outExtentMap[self.pluginParam.getAreaID()]['ymax'])
            area_extent1 = (105, 0, 123, 25)
            area_def = create_area_def('china',
                                       {'EPSG': 4326},
                                       area_extent=area_extent,
                                       units='degrees',
                                       resolution=res
                                       )
            area_def1 = create_area_def('nanhai',
                                        {'EPSG': 4326},
                                        area_extent=area_extent1,
                                        units='degrees',
                                        resolution=res
                                        )
            decorate1 = {'decorate': [
                {'text': {'txt': "南海诸岛",
                          'cursor': [600, 2000],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 280,
                          'height': 280,
                          'bg': None,
                          'line': 'white'}}]}
            overlay1 = {
                'coast_dir': r'D:\001Project\006SanQing\RSPlatForm\Depend\SanQing\Other\othershp\gshhs',
                'color': (255, 242, 0),
                'width': 7,
                'resolution': 'h',
            }
            overlay = {
                'coast_dir': r'D:\001Project\006SanQing\RSPlatForm\Depend\SanQing\Other\othershp\gshhs',
                'color': (255, 242, 0),
                'width': 5,
                'resolution': 'h',
            }
            issue = self.pluginParam.getIssue()
            date_format = "%Y%m%d%H%M"
            filetime = datetime.datetime.strptime(issue, date_format)
            delt_BJ = datetime.timedelta(hours=8)
            filetime_ = filetime - delt_BJ
            filenames = find_files_and_readers(start_time=filetime_,
                                               end_time=filetime_,
                                               base_dir=inputFloder,
                                               reader='ahi_hsd')
            scn = Scene(reader='ahi_hsd', filenames=filenames)
            scn.load([composite])
            lcn = scn.resample(area_def)
            lcn1 = scn.resample(area_def1)
            fileAry = BaseFile.getFilePathInfo(inputFloder, True)
            lcn1.save_dataset(composite, filename=self.tempFolder + "/" + fileAry[1] + 'nanhai.png', overlay=overlay1, decorate=decorate1)

            decorate = {'decorate': [
                {'logo': {'logo_path': self.tempFolder + "/" + fileAry[1] + 'nanhai.png', 'height': 743,
                          'cursor': [0, 2950],
                          'bg': 'white', 'bg_opacity': 255}},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/legend3.png", 'height': 712,
                          'align': {'top_bottom': 'bottom', 'left_right': 'left'},
                          'bg': 'white', 'bg_opacity': 255}},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [4258, 1672],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [4340, 1766],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [4068, 1875],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [3876, 1892],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [3786, 1597],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [4961, 1500],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [5151, 1290],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [5284, 1105],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [4766, 2556],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [4497, 2475],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [4635, 2653],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [4347, 2493],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [4549, 3072],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [4209, 2812],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [4320, 2013],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [3985, 2204],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [4049, 2623],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [3918, 2859],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [3946, 3368],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [3451, 3399],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [3654, 3676],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [3028, 2613],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [3271, 2724],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [3291, 3022],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [2890, 3175],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [1733, 2714],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [3514, 2253],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [2995, 2073],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [2798, 2019],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [3247, 1833],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [1390, 1300],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [4771, 3175],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [3975, 3459],
                          'bg': None, }},
                {'logo': {'logo_path': "D:/001Project/006SanQing/RSPlatForm/Depend/SanQing/Pic/city_legend_white.png", 'height': 160,
                          'cursor': [4025, 3461],
                          'bg': None, }},
                {'text': {'txt': "北京时：" + filetime.strftime("%Y-%m-%d %H:%M"),
                          'align': {'top_bottom': 'top', 'left_right': 'right'},
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 140,
                          'height': 140,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "北京",
                          'cursor': [4508, 1507],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "天津",
                          'cursor': [4590, 1586],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "石家庄",
                          'cursor': [4318, 1695],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "太原",
                          'cursor': [4086, 1712],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "呼和浩特",
                          'cursor': [4036, 1417],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "沈阳",
                          'cursor': [5211, 1320],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "长春",
                          'cursor': [5401, 1110],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "哈尔滨",
                          'cursor': [5534, 925],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "上海",
                          'cursor': [5016, 2376],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "南京",
                          'cursor': [4747, 2295],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "杭州",
                          'cursor': [4885, 2473],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "合肥",
                          'cursor': [4547, 2303],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "福州",
                          'cursor': [4799, 2892],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "南昌",
                          'cursor': [4459, 2632],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "济南",
                          'cursor': [4570, 1833],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "郑州",
                          'cursor': [4235, 2024],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "北京",
                          'cursor': [4508, 1507],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "武汉",
                          'cursor': [4299, 2443],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "长沙",
                          'cursor': [4168, 2679],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "广州",
                          'cursor': [4196, 3188],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "南宁",
                          'cursor': [3701, 3219],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "海口",
                          'cursor': [3904, 3496],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "成都",
                          'cursor': [3278, 2433],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "重庆",
                          'cursor': [3521, 2544],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "贵阳",
                          'cursor': [3541, 2842],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "昆明",
                          'cursor': [3140, 2995],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "拉萨",
                          'cursor': [1983, 2534],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "西安",
                          'cursor': [3764, 2073],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "兰州",
                          'cursor': [3245, 1893],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "西宁",
                          'cursor': [3048, 1839],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "银川",
                          'cursor': [3497, 1653],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "乌鲁木齐",
                          'cursor': [1630, 1120],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "台北",
                          'cursor': [5021, 2995],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "澳门",
                          'cursor': [4055, 3309],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
                {'text': {'txt': "香港",
                          'cursor': [4295, 3271],
                          'font': r"C://Windows//Fonts//simhei.ttf",
                          'font_size': 75,
                          'height': 75,
                          'bg': None,
                          'line': 'white'}},
            ]}
            outpngpath = self.curProdFolder + '//' + self.pluginParam.getAreaID() + '.png'
            outtranspngpath = self.curProdFolder + '//' + self.pluginParam.getAreaID() + '_transparent.png'
            lcn.save_dataset(composite, filename=outpngpath, decorate=decorate, overlay=overlay)
            lcn.save_dataset(composite, filename=outtranspngpath)
            print("done")
            # lcn.save_dataset(composite, filename='{name}_{start_time:%Y%m%d_%H%M%S}.tiff')

            self.rsOutMap['OUTPNGPATH'] = outpngpath
            self.rsOutMap['OUTTRANSPNGPATH'] = outtranspngpath
            suffix = BaseFile.getFilePathInfo(outpngpath, True)[2]
            self.outFileMap[self.pluginParam.getAreaID()] = [({"type": suffix, "file": outpngpath})]
            suffix = BaseFile.getFilePathInfo(outtranspngpath, True)[2]
            self.outFileMap[self.pluginParam.getAreaID()].append({"type": suffix, "file": outtranspngpath})
            print("专题图生产完成")
            BaseFile.appendLogInfo(self.logPath, str(float(50) + 10) + "%", "专题图生产完成...")
        except:
            BaseFile.appendLogInfo(self.logPath, "90%", 'faild')
            return False

    def doStatisComp(self, tempDir, tifPath, curProNumber):
        """统计分析"""
        staMap = self.dostaMapInit(tifPath)

        # #【1】统计，【临时文件夹，tif文件，最小的行政区划，区域的等级】
        # ConstParam.NORMALSTATISTICS（正常统计）, ConstParam.GRADATIONSTATISTICS（分级统计）, ConstParam.ALLSTATISTICS（分级统计 + 正常统计）
        # self.areaStatis(tempDir, tifPath, ConstParam.ALLSTATISTICS)

        # 【2】专题图
        curProNumber = curProNumber + 10
        # self.creatPic(tifPath, staMap, str(float('%.2f' % curProNumber)))

        # 【3】裁切
        curProNumber = curProNumber + 10
        # self.areaClipTif(tifPath, staMap, str(float('%.2f' % curProNumber)))

        return True


