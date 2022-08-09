# encoding: utf-8
"""
@author: DYX
@file: OsgeoTools.py
@time: 2020/10/16 15:43
@desc:
"""

from osgeo import ogr, gdal


class OsgeoTools:
    """地理信息操作工具集合"""

    @staticmethod
    def CalMapExtent(shaFile, Margin):
        """获取shp矢量四至范围"""
        try:
            datasource = ogr.Open(shaFile)
            layer = datasource.GetLayer(0)
            extent = layer.GetExtent()

            minLon = extent[0]
            maxLon = extent[1]
            Width = maxLon - minLon
            minLat = extent[2]
            maxLat = extent[3]
            Height = maxLat - minLat
            ShpExtent = [minLon, maxLon, minLat, maxLat]

            ratio = 1 - Margin / 100.

            minLon = minLon + Width * ratio
            maxLon = maxLon - Width * ratio
            minLat = minLat + Height * ratio
            maxLat = maxLat - Height * ratio
            MapExtent = [minLon, maxLon, minLat, maxLat]

            return ShpExtent, MapExtent
        except:
            return

    @staticmethod
    def CalPageLayout(bbox, Margin, mapW, printResolution, DataFrame, PageSetup):
        """重新计算页面参数-ShpExtent、MapExtent、figsize
        ``bbox: shapefile 类，    第i个shape类的 左下角 Lon,Lat  +   右上角 Lon,Lat
        ``Margin: 中间地图放大系数
        ``mapW: 中间地图宽度，默认是10
        ``printResolution: dpi
        ``DataFrame:
        ``PageSetup
        """
        try:
            minLon = bbox[0]
            maxLon = bbox[2]
            Width = maxLon - minLon
            minLat = bbox[1]
            maxLat = bbox[3]
            Height = maxLat - minLat
            ShpExtent = [minLon, maxLon, minLat, maxLat]

            ratio = 1 - Margin / 100.
            minLon = minLon + Width * ratio
            maxLon = maxLon - Width * ratio
            minLat = minLat + Height * ratio
            maxLat = maxLat - Height * ratio
            MapExtent = [minLon, maxLon, minLat, maxLat]

            DataFrame['Extent']['xmin'] = MapExtent[0]
            DataFrame['Extent']['xmax'] = MapExtent[1]
            DataFrame['Extent']['ymin'] = MapExtent[2]
            DataFrame['Extent']['ymax'] = MapExtent[3]
            DataFrame['ShpExtent'] = {'xmin': ShpExtent[0],
                                      'xmax': ShpExtent[1],
                                      'ymin': ShpExtent[2],
                                      'ymax': ShpExtent[3]}

            # figsize计算
            ratio = (MapExtent[1] - MapExtent[0]) / (MapExtent[3] - MapExtent[2])
            mapPosition = DataFrame['positionOnPage']

            mapH = mapW / ratio

            figW = mapW / mapPosition[2] * printResolution / 100.
            figH = mapH / mapPosition[3] * printResolution / 100.
            PageSetup['size'] = (figW, figH)

            return DataFrame, PageSetup
        except:
            return

    @staticmethod
    def read_tiff(path, idx_band, scale=None, buf_xsize=None, buf_ysize=None):
        """
        读取 TIFF 文件
        :param path: str，unicode，dataset
        :param idx_band: str，unicode，int
        :param scale: 重采样系数     # 已知原数据分辨率
        :param buf_xsize: 重采样列数     # 已知目标数据的行列
        :param buf_ysize:重采样行数
        :return:
        """

        # 参数类型检查
        if isinstance(path, gdal.Dataset):
            dataset = path
        else:
            dataset = gdal.Open(path)

        if dataset:
            XSize = dataset.RasterXSize  # 栅格矩阵的列数
            YSize = dataset.RasterYSize  # 栅格矩阵的行数
            bands = dataset.RasterCount  # 波段数
            proj = dataset.GetProjection()  # 获取投影信息
            geotrans = list(dataset.GetGeoTransform())  # 获取仿射矩阵信息

            if not (scale) is None:
                scale = float(scale)
            if not (buf_xsize) is None:
                buf_xsize = int(buf_xsize)
            if not (buf_ysize) is None:
                buf_ysize = int(buf_ysize)

            if not (scale) is None and (buf_xsize is None and buf_ysize is None):
                XSize = int(XSize * scale)
                YSize = int(YSize * scale)
                geotrans[1] = geotrans[1] / scale
                geotrans[5] = geotrans[5] / scale
            elif not (buf_xsize) is None and not (buf_ysize) is None and scale is None:
                geotrans[1] = geotrans[1] / (buf_xsize / XSize)
                geotrans[5] = geotrans[5] / (buf_ysize / YSize)
                XSize = buf_xsize
                YSize = buf_ysize

            idx_band = int(idx_band)
            if idx_band <= bands:
                in_band = dataset.GetRasterBand(idx_band)
                data = in_band.ReadAsArray(0, 0, buf_xsize=XSize, buf_ysize=YSize)  # 获取数据
                # minV, maxV = in_band.ComputeRasterMinMax()
                return data, geotrans
            else:
                print('error in read tiff')
        else:
            print('error in read tiff')

    @staticmethod
    def readTifByShp(tifFile, shpFile, key, value, scale):
        """矢量数据裁剪"""
        dataset = gdal.Open(tifFile)
        XSize = dataset.RasterXSize
        YSize = dataset.RasterYSize

        scale = int(scale)

        dsScale = gdal.Warp("", dataset, format="MEM",
                            width=XSize * scale, height=YSize * scale,
                            resampleAlg=gdal.GRA_Bilinear,)

        cutline_where_args = key + " = " + "\'" + str(value) + "\'"  # filter continue
        output_bounds_args = None
        outDs = gdal.Warp("", dsScale, format="MEM", cutlineDSName=shpFile,
                          cutlineWhere=cutline_where_args, outputBounds=output_bounds_args,
                          width=XSize * scale, height=YSize * scale,
                          resampleAlg=gdal.GRA_Bilinear,
                          )
        # outDs = gdal.Warp("", dsScale, format="MEM",
        #                   cutlineWhere=cutline_where_args, outputBounds=output_bounds_args,
        #                   width=XSize * scale, height=YSize * scale,
        #                   resampleAlg=gdal.GRA_Bilinear,
        #                   )
        data, geotrans = OsgeoTools.read_tiff(outDs, 1)
        return data, geotrans
