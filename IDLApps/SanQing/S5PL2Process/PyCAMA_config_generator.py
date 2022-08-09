#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import plistlib
import sys

# Unicode characters: http://www.fileformat.info/info/unicode/char/search.htm
from pycama import __version__

if __name__ == "__main__":
    d = {
        'general_settings': {
            # 'actions' are the keys to extract certain information. These can be processing mode dependent.
            # currently defined actions are 'world', 'histogram', 'along_track', 'scatter', 'outline', 'events' and 'irradiance'
            'actions': {'NRTI': ['world', 'histogram', 'along_track', 'outline', 'events', 'irradiance'],
                        'OFFL': ['world', 'histogram', 'along_track', 'scatter', 'outline', 'events', 'irradiance'],
                        'RPRO': ['world', 'histogram', 'along_track', 'scatter', 'outline', 'events', 'irradiance'],
                        'TEST': ['world', 'histogram', 'along_track', 'scatter', 'outline', 'events', 'irradiance'],
                        'OPER': ['world', 'histogram', 'along_track', 'scatter', 'outline', 'events', 'irradiance']
                        },
            'histogram_bincount': 100,
            'include_data': False,
            'interval_duration': 'P1D',  # default aggregation period is 1 day.
            'reference_time': 'ref',
        # 'start' (begin of granule), 'stop', 'end' (both end of granule), 'ref' (reference time), 'mid' (middle of granule)
            'spatial_resolution': 0.255,
            'synchronize': True,
            'full_synchronize': False,
            'pycama_version': __version__,
            'scanline_dimension': 'scanline',
            'warnings_limit': 5000,  # when exceeding this limit an error is generated.
            # Optional: map configuration names to actual product mnemonics.
            # product_mapping': {'internal_name':'real_name'}
            'variables':
                [
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-90.0, 90.0],
                        'field_name': 'latitude',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'latitude',
                        'histogram_bincount': 90,
                        'show': False,
                        'title': 'Latitude',
                        'units': "\u00B0N"
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 90.0],
                        'field_name': 'solar_zenith_angle',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'solar_zenith_angle',
                        'histogram_bincount': 45,
                        'show': False,
                        'title': 'Solar zenith angle',
                        'units': "\u00B0"
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 90.0],
                        'field_name': 'viewing_zenith_angle',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'viewing_zenith_angle',
                        'histogram_bincount': 45,
                        'show': False,
                        'title': 'Viewing zenith angle',
                        'units': "\u00B0"
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-180.0, 180.0],
                        'field_name': 'longitude',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'longitude',
                        'show': False,
                        'internal_only': True,
                        'title': 'Longitude',
                        'units': "\u00B0E"
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 2 ** 32 - 1],
                        'field_name': 'processing_quality_flags',
                        'flag': True,
                        'log_range': False,
                        'primary_variable': 'processing_quality_flags',
                        'show': False,
                        'internal_only': True,
                        'title': 'Processing quality flags',
                        'units': ""
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 256],
                        'field_name': 'geolocation_flags',
                        'flag': True,
                        'log_range': False,
                        'primary_variable': 'geolocation_flags',
                        'show': False,
                        'internal_only': True,
                        'title': 'Geolocation flags',
                        'units': ""
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 256],
                        'field_name': 'surface_classification',
                        'flag': True,
                        'log_range': False,
                        'primary_variable': 'surface_classification',
                        'show': False,
                        'internal_only': True,
                        'title': 'Surface classification',
                        'units': ""
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 360],
                        'field_name': 'solar_azimuth_angle',
                        'flag': True,
                        'log_range': False,
                        'primary_variable': 'solar_azimuth_angle',
                        'show': False,
                        'internal_only': True,
                        'title': 'Solar azimuth angle',
                        'units': "\u00B0"
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 360],
                        'field_name': 'viewing_azimuth_angle',
                        'flag': True,
                        'log_range': False,
                        'primary_variable': 'viewing_azimuth_angle',
                        'show': False,
                        'internal_only': True,
                        'title': 'Viewing azimuth angle',
                        'units': "\u00B0"
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 1.0],
                        'field_name': 'qa_value',
                        'flag': False,
                        'level3': False,
                        'include_scatter': False,
                        'log_range': False,
                        'primary_variable': 'qa_value',
                        'show': True,
                        'internal_only': False,
                        'title': 'QA value',
                        'units': "1",
                        'transformers':
                            [
                                {
                                    'class': 'transform.Multiplier',
                                    'arguments': {'operator': '/', 'scalefactor': 100.0}
                                },
                            ]
                    }
                ]
        },
        'FRESCO': {
            'contact': 'Maarten Sneep',
            'contact_email': 'maarten.sneep@knmi.nl',
            'developer': 'KNMI',
            'developer_contact': 'tropomi_l2_dev@knmi.nl',
            'variables':
                [
                    {
                        'color_scale': 'viridis',
                        'data_range': [100.0, 1100.0],
                        'field_name': 'cloud_pressure_crb',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_pressure_crb',
                        'secondary_variable': 'cloud_fraction_crb',
                        'show': True,
                        'title': 'Cloud pressure',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Multiplier',
                                    'arguments': {'operator': '/', 'scalefactor': 100.0}
                                },
                            ],
                        'units': 'hPa'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 150.0],
                        'field_name': 'cloud_pressure_crb_precision',
                        'flag': False,
                        'log_range': False,
                        'level3': False,
                        'include_scatter': False,
                        'primary_variable': 'cloud_pressure_crb_precision',
                        'secondary_variable': 'cloud_fraction_crb',
                        'show': True,
                        'title': 'Cloud pressure precision',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Multiplier',
                                    'arguments': {'operator': '/', 'scalefactor': 100.0}
                                },
                            ],
                        'units': 'hPa'
                    },
                    {
                        'color_scale': 'Blues_r',
                        'data_range': [0.0, 1.1],
                        'map_range': [0.0, 1.0],
                        'field_name': 'cloud_fraction_crb',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_fraction_crb',
                        'show': True,
                        'title': 'Cloud fraction',
                        'units': '',
                        'transformers':
                            [
                                {
                                    'class': 'transform.ProcessingQualityFlagsFilter',
                                    'arguments': {'mask': 0xff}
                                }
                            ],
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 0.05],
                        'field_name': 'cloud_fraction_crb_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_fraction_crb_precision',
                        'level3': False,
                        'include_scatter': False,
                        'show': True,
                        'title': 'Cloud fraction precision',
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.0, 1.0],
                        'field_name': 'scene_albedo',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'scene_albedo',
                        'show': True,
                        'title': 'Scene albedo',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 0.05],
                        'field_name': 'scene_albedo_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'scene_albedo_precision',
                        'level3': False,
                        'include_scatter': False,
                        'show': True,
                        'title': 'Scene albedo precision',
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [300.0, 1100.0],
                        'field_name': 'apparent_scene_pressure',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'apparent_scene_pressure',
                        'show': True,
                        'title': 'Apparent scene pressure',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Multiplier',
                                    'arguments': {'operator': '/', 'scalefactor': 100.0}
                                }
                            ],
                        'units': 'hPa'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 100.0],
                        'field_name': 'apparent_scene_pressure_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'apparent_scene_pressure_precision',
                        'level3': False,
                        'include_scatter': False,
                        'show': True,
                        'title': 'Apparent scene pressure precision',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Multiplier',
                                    'arguments': {'operator': '/', 'scalefactor': 100.0}
                                }
                            ],
                        'units': 'hPa'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 30.0],
                        'field_name': 'chi_square',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'chi_square',
                        'level3': False,
                        'show': True,
                        'title': '\u03C7\u00B2',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 12],
                        'field_name': 'number_of_iterations',
                        'flag': False,
                        'log_range': False,
                        'histogram_bincount': 13,
                        'primary_variable': 'number_of_iterations',
                        'level3': False,
                        'show': True,
                        'title': 'Number of iterations',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 5e-8],
                        'field_name': 'fluorescence',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'fluorescence',
                        'show': True,
                        'title': 'Fluorescence',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 2, 'collapse': False}
                                }
                            ],
                        'units': 'mol s\u207B\u00B9 m\u207B\u00B2 nm\u207B\u00B9 sr\u207B\u00B9'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 1e-8],
                        'field_name': 'fluorescence_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'fluorescence_precision',
                        'level3': False,
                        'include_scatter': False,
                        'show': True,
                        'title': 'Fluorescence precision',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 2, 'collapse': False}
                                }
                            ],
                        'units': 'mol s\u207B\u00B9 m\u207B\u00B2 nm\u207B\u00B9 sr\u207B\u00B9'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 5.0e4],
                        'field_name': 'chi_square_fluorescence',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'chi_square_fluorescence',
                        'level3': False,
                        'show': True,
                        'title': '\u03C7\u00B2 of fluorescence retrieval',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 10.0],
                        'field_name': 'degrees_of_freedom_fluorescence',
                        'flag': False,
                        'log_range': False,
                        'histogram_bincount': 21,
                        'primary_variable': 'degrees_of_freedom_fluorescence',
                        'show': True,
                        'level3': False,
                        'title': 'Degrees of freedom for signal of fluorescence retrieval',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 30],
                        'field_name': 'number_of_spectral_points_in_retrieval',
                        'flag': False,
                        'log_range': False,
                        'histogram_bincount': 31,
                        'primary_variable': 'number_of_spectral_points_in_retrieval',
                        'level3': False,
                        'show': True,
                        'title': 'Number of points in the spectrum',
                        'units': ''
                    },
                    {
                        'color_scale': 'seismic',
                        'data_range': [-0.04, 0.04],
                        'field_name': 'wavelength_calibration_offset',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_offset',
                        'level3': False,
                        'show': True,
                        'title': 'Spectral offset (\u03BB(true) \u2212 \u03BB(nominal))',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 0.005],
                        'field_name': 'wavelength_calibration_offset_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_offset_precision',
                        'level3': False,
                        'include_scatter': False,
                        'show': True,
                        'title': 'Precision of spectral offset',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 5.0e4],
                        'field_name': 'wavelength_calibration_chi_square',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_chi_square',
                        'level3': False,
                        'show': True,
                        'title': '\u03C7\u00B2 of wavelength calibration',
                        'units': ''
                    },
                    {
                        'color_scale': 'seismic',
                        'data_range': [-0.1, 0.1],
                        'field_name': 'wavelength_calibration_irradiance_offset',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_irradiance_offset',
                        'show': True,
                        'title': 'Spectral offset irradiance (\u03BB(true) \u2212 \u03BB(nominal))',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 0.1],
                        'field_name': 'wavelength_calibration_irradiance_offset_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_irradiance_offset_precision',
                        'show': True,
                        'title': 'Precision of spectral offset irradiance (\u03BB(true) \u2212 \u03BB(nominal))',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 100.0],
                        'field_name': 'wavelength_calibration_irradiance_chi_square',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_irradiance_chi_square',
                        'show': True,
                        'title': '\u03C7\u00B2 of irradiance wavelength calibration',
                        'units': ''
                    }
                ]
        },
        'OMICLD': {
            'equivalent_product': 'FRESCO'
        },
        'O22CLD': {
            'equivalent_product': 'FRESCO'
        },
        'AER_AI': {
            'contact': 'Deborah Stein-Zweers',
            'contact_email': 'deborah.zweers-stein@knmi.nl',
            'developer': 'KNMI',
            'developer_contact': 'tropomi_l2_dev@knmi.nl',
            'variables':
                [
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-5, 7],
                        'map_range': [-3, 5],
                        'field_name': 'aerosol_index_354_388',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'aerosol_index_354_388',
                        'show': True,
                        'title': 'UV aerosol index (354/388 nm)',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-5, 7],
                        'map_range': [-3, 5],
                        'field_name': 'aerosol_index_340_380',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'aerosol_index_340_380',
                        'show': True,
                        'title': 'UV aerosol index (340/380 nm)',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 2],
                        'field_name': 'aerosol_index_354_388_precision',
                        'flag': False,
                        'log_range': False,
                        'level3': False,
                        'include_scatter': False,
                        'primary_variable': 'aerosol_index_354_388_precision',
                        'show': True,
                        'title': 'Precision of the UV aerosol index (354/388 nm)',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 2],
                        'field_name': 'aerosol_index_340_380_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'aerosol_index_340_380_precision',
                        'level3': False,
                        'include_scatter': False,
                        'show': True,
                        'title': 'Precision of the UV aerosol index (340/380 nm)',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 50],
                        'field_name': 'number_of_spectral_points_in_retrieval',
                        'flag': False,
                        'log_range': False,
                        'level3': False,
                        'include_scatter': False,
                        'histogram_bincount': 51,
                        'primary_variable': 'number_of_spectral_points_in_retrieval',
                        'show': True,
                        'title': 'Number of points in the spectrum',
                        'units': ''
                    },
                    {
                        'color_scale': 'seismic',
                        'data_range': [-0.04, 0.04],
                        'field_name': 'wavelength_calibration_offset',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_offset',
                        'level3': False,
                        'show': True,
                        'title': 'Spectral offset (\u03BB(true) \u2212 \u03BB(nominal))',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 0.001],
                        'field_name': 'wavelength_calibration_offset_precision',
                        'flag': False,
                        'level3': False,
                        'include_scatter': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_offset_precision',
                        'show': True,
                        'title': 'Precision of spectral offset',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 2.5e6],
                        'field_name': 'wavelength_calibration_chi_square',
                        'flag': False,
                        'log_range': False,
                        'level3': False,
                        'primary_variable': 'wavelength_calibration_chi_square',
                        'show': True,
                        'title': '\u03C7\u00B2 of wavelength calibration',
                        'units': ''
                    },
                    {
                        'color_scale': 'seismic',
                        'data_range': [-0.1, 0.1],
                        'field_name': 'wavelength_calibration_irradiance_offset',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_irradiance_offset',
                        'show': True,
                        'title': 'Spectral offset irradiance (\u03BB(true) \u2212 \u03BB(nominal))',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 0.1],
                        'field_name': 'wavelength_calibration_irradiance_offset_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_irradiance_offset_precision',
                        'show': True,
                        'title': 'Precision of spectral offset irradiance (\u03BB(true) \u2212 \u03BB(nominal))',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 100.0],
                        'field_name': 'wavelength_calibration_irradiance_chi_square',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_irradiance_chi_square',
                        'show': True,
                        'title': '\u03C7\u00B2 of irradiance wavelength calibration',
                        'units': ''
                    }
                ]
        },
        'AER_LH': {
            'contact': 'Martin de Graaf',
            'contact_email': 'martin.de.graaf@knmi.nl',
            'developer': 'KNMI',
            'developer_contact': 'tropomi_l2_dev@knmi.nl',
            'full_synchronize': True,
            'variables':
                [
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [100.0, 1100.0],
                        'field_name': 'aerosol_mid_pressure',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'aerosol_mid_pressure',
                        'show': True,
                        'title': 'Aerosol mid pressure',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Multiplier',
                                    'arguments': {'operator': '/', 'scalefactor': 100.0}
                                }
                            ],
                        'units': 'hPa'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 400.0],
                        'field_name': 'aerosol_mid_pressure_precision',
                        'flag': False,
                        'log_range': False,
                        'level3': False,
                        'include_scatter': False,
                        'primary_variable': 'aerosol_mid_pressure_precision',
                        'show': True,
                        'title': 'Aerosol mid pressure precision',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Multiplier',
                                    'arguments': {'operator': '/', 'scalefactor': 100.0}
                                }
                            ],
                        'units': 'hPa'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 100],
                        'field_name': 'number_of_spectral_points_in_retrieval',
                        'flag': False,
                        'log_range': False,
                        'histogram_bincount': 101,
                        'level3': False,
                        'primary_variable': 'number_of_spectral_points_in_retrieval',
                        'show': True,
                        'title': 'Number of points in the spectrum',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 10],
                        'field_name': 'number_of_iterations',
                        'flag': False,
                        'log_range': False,
                        'histogram_bincount': 11,
                        'level3': False,
                        'include_scatter': False,
                        'primary_variable': 'number_of_iterations',
                        'show': True,
                        'title': 'Number of iterations',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 10.0],
                        'field_name': 'degrees_of_freedom',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'degrees_of_freedom',
                        'level3': False,
                        'include_scatter': False,
                        'show': True,
                        'title': 'Degrees of freedom for signal',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 200.0],
                        'field_name': 'root_mean_square_error_of_fit',
                        'flag': False,
                        'log_range': False,
                        'level3': False,
                        'primary_variable': 'root_mean_square_error_of_fit',
                        'show': True,
                        'title': 'RMS deviation of fit',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 100.0],
                        'field_name': 'chi_square',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'chi_square',
                        'level3': False,
                        'show': True,
                        'title': '\u03C7\u00B2',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 100.0],
                        'field_name': 'chi_square_reflectance',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'chi_square_reflectance',
                        'level3': False,
                        'show': True,
                        'title': '\u03C7\u00B2 of reflectance',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 100.0],
                        'field_name': 'chi_squared_statevector',
                        'flag': False,
                        'log_range': False,
                        'level3': False,
                        'primary_variable': 'chi_squared_statevector',
                        'show': True,
                        'title': '\u03C7\u00B2 of state vector',
                        'units': ''
                    }
                ]
        },
        'CH4___': {
            'contact': 'Jochen Landgraf',
            'contact_email': 'J.Landgraf@sron.nl',
            'developer': 'KNMI',
            'developer_contact': 'tropomi_l2_dev@knmi.nl',
            'variables':
                [
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [1500.0, 2000.0],
                        'field_name': 'methane_mixing_ratio',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'methane_mixing_ratio',
                        'show': True,
                        'title': 'Mole fraction of CH\u2084',
                        'units': 'parts per 10\u2079'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 20.0],
                        'field_name': 'methane_mixing_ratio_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'methane_mixing_ratio_precision',
                        'show': True,
                        'title': 'Precision of mole fraction of CH\u2084',
                        'units': 'parts per 10\u2079'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 20.0],
                        'field_name': 'dry_air_summation',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'dry_air_subcolumns',
                        'show': False,
                        'title': 'Dry air summation',
                        'units': 'parts per 10\u2079',
                        'transformers': [
                            {
                                'class': 'transform.Select',
                                'arguments': {'dimension': -1, 'sum': True}
                            }
                        ]
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 20.0],
                        'field_name': 'xch4_prior_summation',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'methane_profile_apriori',
                        'show': False,
                        'title': 'Dry air summation',
                        'units': 'parts per 10\u2079',
                        'transformers': [
                            {
                                'class': 'transform.Select',
                                'arguments': {'dimension': -1, 'sum': True}
                            }
                        ]
                    },
                    {
                        'color_scale': 'seismic',
                        'data_range': [-15.0, 15.0],
                        'field_name': 'XCH4_prior',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': '(xch4_prior_summation/dry_air_summation)*1e9',
                        'show': False,
                        'title': '$\Delta$ XCH$_4$',
                        'units': '%'
                    },
                    {
                        'color_scale': 'seismic',
                        'data_range': [-15.0, 15.0],
                        'field_name': 'delta_XCH4',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': '100*((methane_mixing_ratio/XCH4_prior)-1)',
                        'show': True,
                        'title': '$\Delta$ XCH$_4$',
                        'units': '%'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 20.0],
                        'field_name': 'methane_mixing_ratio_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'methane_mixing_ratio_precision',
                        'show': True,
                        'title': 'Precision of mole fraction of CH\u2084',
                        'units': 'parts per 10\u2079'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [1500.0, 2000.0],
                        'field_name': 'methane_mixing_ratio_bias_corrected',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'methane_mixing_ratio_bias_corrected',
                        'show': True,
                        'title': 'Bias corrected mole fraction of CH\u2084',
                        'units': 'parts per 10\u2079'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [500, 1000],
                        'field_name': 'number_of_spectral_points_in_retrieval',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'number_of_spectral_points_in_retrieval',
                        'show': True,
                        'level3': False,
                        'title': 'Number of points in the spectrum',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 200],
                        'field_name': 'number_of_spectral_points_in_retrieval_NIR',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'number_of_spectral_points_in_retrieval_NIR',
                        'show': True,
                        'level3': False,
                        'title': 'Number of points in the spectrum (NIR)',
                        'units': ''
                    },
                    {
                        'color_scale': 'seismic',
                        'data_range': [-0.1, 0.1],
                        'field_name': 'wavelength_calibration_offset_SWIR',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_offset_SWIR',
                        'level3': False,
                        'show': True,
                        'title': 'Spectral offset SWIR (\u03BB(true) \u2212 \u03BB(nominal))',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'seismic',
                        'data_range': [-0.1, 0.1],
                        'field_name': 'wavelength_calibration_offset_NIR',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_offset_NIR',
                        'show': True,
                        'level3': False,
                        'title': 'Spectral offset NIR (\u03BB(true) \u2212 \u03BB(nominal))',
                        'units': 'nm'
                    },
                    # {
                    #     'color_scale': 'nipy_spectral',
                    #     'data_range': [0.0, 10000.0],
                    #     'field_name': 'chi_square',
                    #     'flag': False,
                    #     'log_range': False,
                    #     'primary_variable': 'chi_square',
                    #     'show': True,
                    #     'title': '\u03C7\u00B2',
                    #     'units': ''
                    # },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 10000.0],
                        'field_name': 'chi_square_SWIR',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'chi_square_SWIR',
                        'show': True,
                        'level3': False,
                        'title': '\u03C7\u00B2 (SWIR)',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 10000.0],
                        'field_name': 'chi_square_NIR',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'chi_square_NIR',
                        'show': True,
                        'level3': False,
                        'title': '\u03C7\u00B2 (NIR)',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [5.0, 20.0],
                        'field_name': 'degrees_of_freedom',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'degrees_of_freedom',
                        'show': True,
                        'level3': False,
                        'title': 'Degrees of freedom',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 5.0],
                        'field_name': 'degrees_of_freedom_methane',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'degrees_of_freedom_methane',
                        'show': True,
                        'level3': False,
                        'title': 'Degrees of freedom for CH\u2084',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 5.0],
                        'field_name': 'degrees_of_freedom_aerosol',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'degrees_of_freedom_aerosol',
                        'show': True,
                        'level3': False,
                        'title': 'Degrees of freedom for aerosol',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 30],
                        'field_name': 'number_of_iterations',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'number_of_iterations',
                        'histogram_bincount': 31,
                        'level3': False,
                        'show': True,
                        'title': 'Number of iterations',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-1.0e-8, 1e-8],
                        'field_name': 'fluorescence',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'fluorescence',
                        'show': True,
                        'title': 'Fluorescence',
                        'units': 'mol s\u207B\u00B9 m\u207B\u00B2 nm\u207B\u00B9 sr\u207B\u00B9'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-1.0e-8, 1e-8],
                        'field_name': 'fluorescence_apriori',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'fluorescence_apriori',
                        'show': True,
                        'level3': False,
                        'title': 'Fluorescence a priori',
                        'units': 'mol s\u207B\u00B9 m\u207B\u00B2 nm\u207B\u00B9 sr\u207B\u00B9'
                    }
                ]
        },
        'CLOUD_': {
            'contact': 'Ronny Lutz',
            'contact_email': 'ronny.lutz@dlr.de',
            'developer': 'DLR',
            'developer_contact': 'mattia.pedergnana@dlr.de',
            'variables':
                [
                    {
                        'color_scale': 'Blues_r',
                        'data_range': [0.0, 1.0],
                        'field_name': 'cloud_fraction',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_fraction',
                        'show': True,
                        'title': 'Radiometric cloud fraction',
                        'units': ''
                    },
                    {
                        'color_scale': 'Reds',
                        'data_range': [0.0, 1E-3],
                        'field_name': 'cloud_fraction_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_fraction_precision',
                        'show': True,
                        'title': 'Precision of the radiometric cloud fraction',
                        'units': ''
                    },
                    {
                        'color_scale': 'jet_r',
                        'data_range': [100.0, 1100.0],
                        'field_name': 'cloud_top_pressure',
                        'flag': False,
                        'log_range': True,
                        'primary_variable': 'cloud_top_pressure',
                        'show': True,
                        'title': 'Cloud top pressure',
                        'units': 'hPa',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Multiplier',
                                    'arguments': {'operator': '/', 'scalefactor': 100.0}
                                }
                            ],
                    },
                    {
                        'color_scale': 'Reds',
                        'data_range': [0.0, 75.0],
                        'field_name': 'cloud_top_pressure_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_top_pressure_precision',
                        'show': True,
                        'title': 'Cloud top pressure precision',
                        'units': 'hPa',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Multiplier',
                                    'arguments': {'operator': '/', 'scalefactor': 100.0}
                                }
                            ],
                    },
                    {
                        'color_scale': 'jet',
                        'data_range': [0.0, 1.5E4],
                        'field_name': 'cloud_top_height',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_top_height',
                        'show': True,
                        'title': 'Cloud top height',
                        'units': 'm',
                    },
                    {
                        'color_scale': 'Reds',
                        'data_range': [0.0, 1000.],
                        'field_name': 'cloud_top_height_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_top_height_precision',
                        'show': True,
                        'title': 'Cloud top height precision',
                        'units': 'm',
                    },
                    {
                        'color_scale': 'jet',
                        'data_range': [0.0, 30.0],
                        'field_name': 'cloud_optical_thickness',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_optical_thickness',
                        'show': True,
                        'title': 'Cloud optical thickness',
                        'units': ''
                    },
                    {
                        'color_scale': 'Reds',
                        'data_range': [1.0, 2.0],
                        'field_name': 'cloud_optical_thickness_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_optical_thickness_precision',
                        'show': True,
                        'title': 'Cloud optical thickness precision',
                        'units': ''
                    },
                    {
                        'color_scale': 'Blues_r',
                        'data_range': [0.0, 1.0],
                        'field_name': 'cloud_fraction_crb',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_fraction_crb',
                        'show': True,
                        'title': 'Cloud fraction (CRB)',
                        'units': ''
                    },
                    {
                        'color_scale': 'Reds',
                        'data_range': [0.0, 1E-3],
                        'field_name': 'cloud_fraction_crb_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_fraction_crb_precision',
                        'show': True,
                        'title': 'Precision of the cloud fraction (CRB)',
                        'units': ''
                    },
                    {
                        'color_scale': 'jet_r',
                        'data_range': [100.0, 1100.0],
                        'field_name': 'cloud_pressure_crb',
                        'flag': False,
                        'log_range': True,
                        'primary_variable': 'cloud_pressure_crb',
                        'show': True,
                        'title': 'Cloud pressure (CRB)',
                        'units': 'hPa',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Multiplier',
                                    'arguments': {'operator': '/', 'scalefactor': 100.0}
                                }
                            ],
                    },
                    {
                        'color_scale': 'Reds',
                        'data_range': [0.0, 75.0],
                        'field_name': 'cloud_pressure_crb_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_pressure_crb_precision',
                        'show': True,
                        'title': 'Cloud pressure precision (CRB)',
                        'units': 'hPa',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Multiplier',
                                    'arguments': {'operator': '/', 'scalefactor': 100.0}
                                }
                            ],
                    },
                    {
                        'color_scale': 'jet',
                        'data_range': [0.0, 1.5E4],
                        'field_name': 'cloud_height_crb',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_height_crb',
                        'show': True,
                        'title': 'Cloud height (CRB)',
                        'units': 'm',
                    },
                    {
                        'color_scale': 'Reds',
                        'data_range': [0.0, 1000.],
                        'field_name': 'cloud_height_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_height_crb_precision',
                        'show': True,
                        'title': 'Cloud height precision (CRB)',
                        'units': 'm',
                    },
                    {
                        'color_scale': 'Blues',
                        'data_range': [0.0, 1.0],
                        'field_name': 'cloud_albedo_crb',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_albedo_crb',
                        'show': True,
                        'title': 'Cloud albedo (CRB)',
                        'units': ''
                    },
                    {
                        'color_scale': 'Reds',
                        'data_range': [0.0, 0.007],
                        'field_name': 'cloud_albedo_crb_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cloud_albedo_crb_precision',
                        'show': True,
                        'title': 'Precision of the cloud albedo (CRB)',
                        'units': ''
                    },
                    {
                        'color_scale': 'Blues',
                        'data_range': [0.0, 1.0],
                        'field_name': 'surface_albedo_fitted',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'surface_albedo_fitted',
                        'show': True,
                        'include_scatter': False,
                        'Level3': False,
                        'title': 'Fitted surface albedo',
                        'units': ''
                    },
                    {
                        'color_scale': 'Reds',
                        'data_range': [0.0, 0.005],
                        'field_name': 'surface_albedo_fitted_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'surface_albedo_fitted_precision',
                        'show': True,
                        'include_scatter': False,
                        'Level3': False,
                        'title': 'Precision of the fitted surface albedo',
                        'units': ''
                    },
                    {
                        'color_scale': 'Blues',
                        'data_range': [0.0, 1.0],
                        'field_name': 'surface_albedo_fitted_crb',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'surface_albedo_fitted_crb',
                        'show': True,
                        'include_scatter': False,
                        'Level3': False,
                        'title': 'Fitted surface albedo (CRB)',
                        'units': ''
                    },
                    {
                        'color_scale': 'Reds',
                        'data_range': [0.0, 0.005],
                        'field_name': 'surface_albedo_fitted_crb_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'surface_albedo_fitted_crb_precision',
                        'show': True,
                        'include_scatter': False,
                        'Level3': False,
                        'title': 'Precision of the fitted surface albedo (CRB)',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 100],
                        'field_name': 'number_of_iterations',
                        'flag': False,
                        'log_range': False,
                        'histogram_bincount': 71,
                        'primary_variable': 'number_of_iterations',
                        'show': True,
                        'include_scatter': False,
                        'Level3': False,
                        'title': 'Number of iterations for the wavelength calibration',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 1000],
                        'field_name': 'calibration_subwindows_shift',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'calibration_subwindows_shift',
                        'show': True,
                        'title': 'Wavelength calibration subwindow shift',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 1000],
                        'field_name': 'calibration_subwindows_squeeze',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'calibration_subwindows_squeeze',
                        'show': True,
                        'title': 'Wavelength calibration subwindow squeeze',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 1000],
                        'field_name': 'calibration_polynomial_coefficients',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'calibration_polynomial_coefficients',
                        'show': True,
                        'title': 'Wavelength calibration polynomian coefficients',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 1000],
                        'field_name': 'calibration_subwindows_root_mean_square',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'calibration_subwindows_root_mean_square',
                        'show': True,
                        'title': 'Wavelength calibration subwindows RMS',
                        'units': ''
                    },
                    {
                        'color_scale': 'Reds',
                        'data_range': [0., .1],
                        'field_name': 'fitted_root_mean_square',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'fitted_root_mean_square',
                        'show': True,
                        'include_scatter': False,
                        'title': 'RMS',
                        'units': ''
                    }, {
                    'color_scale': 'Reds_r',
                    'data_range': [0, 5],
                    'field_name': 'degrees_of_freedom',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'degrees_of_freedom',
                    'show': True,
                    'include_scatter': False,
                    'title': 'Degrees of freedom',
                    'units': ''
                }, {
                    'color_scale': 'Reds_r',
                    'data_range': [2, 12],
                    'field_name': 'shannon_information_content',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'shannon_information_content',
                    'show': True,
                    'include_scatter': False,
                    'title': 'Shannon information content',
                    'units': ''
                }, {
                    'color_scale': 'Reds',
                    'data_range': [0, 3000],
                    'field_name': 'condition_number',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'condition_number',
                    'show': True,
                    'include_scatter': False,
                    'Level3': False,
                    'title': 'Condition number',
                    'units': ''
                }, {
                    'color_scale': 'Reds',
                    'data_range': [5.0e-6, 4.0e-5],
                    'field_name': 'regularization_parameter',
                    'flag': False,
                    'log_range': True,
                    'primary_variable': 'regularization_parameter',
                    'show': True,
                    'include_scatter': False,
                    'Level3': False,
                    'title': 'Regularization parameter',
                    'units': ''
                }, {
                    'color_scale': 'RdBu',
                    'data_range': [-0.03, 0.03],
                    'field_name': 'wavelength_shift',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'wavelength_shift',
                    'show': True,
                    'include_scatter': False,
                    'Level3': False,
                    'title': 'Fitting wavelength shift',
                    'units': 'nm'
                }
                    # ,{
                    # 'color_scale': 'nipy_spectral',
                    # 'data_range': [0, 1000],
                    # 'field_name': 'fitting_squeeze',
                    # 'flag': False,
                    # 'log_range': False,
                    # 'primary_variable': 'fitting_squeeze',
                    # 'show': True,
                    # 'title': 'Fitting squeeze',
                    # 'units': ''
                    # },{
                    # 'color_scale': 'nipy_spectral',
                    # 'data_range': [0, 1000],
                    # 'field_name': 'cost_function',
                    # 'flag': False,
                    # 'log_range': False,
                    # 'primary_variable': 'cost_function',
                    # 'show': True,
                    # 'title': 'Cost function',
                    # 'units': ''
                    # }
                ]
        },
        'CO____': {
            'contact': 'Jochen Landgraf',
            'contact_email': 'J.Landgraf@sron.nl',
            'developer': 'KNMI',
            'developer_contact': 'tropomi_l2_dev@knmi.nl',
            'variables':
                [
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.01, 0.07],
                        'field_name': 'carbonmonoxide_total_column',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'carbonmonoxide_total_column',
                        'show': True,
                        'title': 'CO total vertical column',
                        'units': 'mol m\u207B\u00B2'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 0.007],
                        'field_name': 'carbonmonoxide_total_column_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'carbonmonoxide_total_column_precision',
                        'show': True,
                        'level3': False,
                        'title': 'CO total vertical column precision',
                        'units': 'mol m\u207B\u00B2'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 200],
                        'field_name': 'number_of_spectral_points_in_retrieval',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'number_of_spectral_points_in_retrieval',
                        'show': True,
                        'level3': False,
                        'title': 'Number of spectral points in retrieval',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 4500],
                        'field_name': 'chi_square',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'chi_square',
                        'show': True,
                        'level3': False,
                        'title': '\u03C7\u00B2',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 10],
                        'field_name': 'degrees_of_freedom',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'degrees_of_freedom',
                        'level3': False,
                        'show': True,
                        'title': 'Degrees of freedom for signal',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 25],
                        'field_name': 'number_of_iterations',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'number_of_iterations',
                        'show': True,
                        'level3': False,
                        'title': 'Number of iterations',
                        'histogram_bincount': 26,
                        'units': ''
                    }
                ]
        },
        'HCHO__': {
            'contact': 'Isabelle De Smedt',
            'contact_email': 'isabelle.desmedt@aeronomie.be',
            'developer': 'DLR',
            'developer_contact': 'mattia.pedergnana@dlr.de',
            'variables':
                [
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0., 5E-4],
                        'field_name': 'formaldehyde_tropospheric_vertical_column',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'formaldehyde_tropospheric_vertical_column',
                        'show': True,
                        'title': 'HCHO vertical column',
                        'units': 'mol m\u207B\u00B2'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0., 5E-4],
                        'field_name': 'formaldehyde_tropospheric_vertical_column_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'formaldehyde_tropospheric_vertical_column_precision',
                        'show': True,
                        'title': 'HCHO vertical column precision',
                        'units': 'mol m\u207B\u00B2'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0., 1.5E-4],
                        'field_name': 'formaldehyde_tropospheric_vertical_column_correction',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'formaldehyde_tropospheric_vertical_column_correction',
                        'show': True,
                        'title': 'HCHO vertical column correction',
                        'units': 'mol m\u207B\u00B2'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-5E-4, 5E-4],
                        'field_name': 'formaldehyde_slant_column_density',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'fitted_slant_columns',
                        'show': True,
                        'title': 'HCHO slant column',
                        'units': 'mol m\u207B\u00B2',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 0}
                                }
                            ]
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 5E-4],
                        'field_name': 'formaldehyde_slant_column_density_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'fitted_slant_columns_precision',
                        'show': True,
                        'title': 'HCHO slant column precision',
                        'units': 'mol m\u207B\u00B2',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 0}
                                }
                            ]
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-5E-4, 5E-4],
                        'field_name': 'formaldehyde_slant_column_density_window1',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'fitted_slant_columns_win1',
                        'show': True,
                        'title': 'HCHO slant column (window1)',
                        'units': 'mol m\u207B\u00B2',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 6}
                                }
                            ]
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 5E-4],
                        'field_name': 'formaldehyde_slant_column_density_window1_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'fitted_slant_columns_win1_precision',
                        'show': True,
                        'title': 'HCHO slant column precision (window1)',
                        'units': 'mol m\u207B\u00B2',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 6}
                                }
                            ]
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 5.0],
                        'field_name': 'formaldehyde_tropospheric_air_mass_factor',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'formaldehyde_tropospheric_air_mass_factor',
                        'show': True,
                        'title': 'Airmass factor total',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 5.0],
                        'field_name': 'formaldehyde_tropospheric_air_mass_factor_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'formaldehyde_tropospheric_air_mass_factor_precision',
                        'show': True,
                        'title': 'Airmass factor total precision',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 5.0],
                        'field_name': 'formaldehyde_clear_air_mass_factor',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'formaldehyde_clear_air_mass_factor',
                        'show': True,
                        'title': 'Airmass factor clear',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 5.0],
                        'field_name': 'formaldehyde_cloudy_air_mass_factor',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'formaldehyde_cloudy_air_mass_factor',
                        'show': True,
                        'title': 'Airmass factor cloud',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 5E-4],
                        'field_name': 'integrated_formaldehyde_profile_apriori',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'formaldehyde_profile_apriori',
                        'secondary_variable': 'surface_pressure',
                        'show': True,
                        'title': 'Integrated a priori HCHO profile',
                        'transformers':
                            [
                                {
                                    'class': 'transform.IntegratedColumn',
                                    'arguments': {'dimension': -1,
                                                  'coefficients_a': 'read_from_file("tm5_constant_a")',
                                                  'coefficients_b': 'read_from_file("tm5_constant_b")'}
                                }
                            ],
                        'units': 'mol m\u207B\u00B2'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-0.02, 0.02],
                        'field_name': 'fitted_wavelength_radiance_shift',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'fitted_radiance_shift',
                        'show': True,
                        'title': 'DOAS fit wavelength shift',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-5E-4, 5E-4],
                        'field_name': 'fitted_wavelength_radiance_squeeze',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'fitted_radiance_squeeze',
                        'show': True,
                        'title': 'DOAS fit wavelength squeeze',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 5E-3],
                        'field_name': 'fitted_root_mean_square',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'fitted_root_mean_square',
                        'show': True,
                        'title': 'DOAS fit RMS',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 0.01],
                        'field_name': 'fitted_root_mean_square_win1',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'fitted_root_mean_square_win1',
                        'show': True,
                        'title': 'DOAS fit RMS (first interval)',
                        'units': ''
                    },
                    # {
                    #     'color_scale': 'nipy_spectral',
                    #     'data_range': [140,160],
                    #     'histogram_bincount': 21,
                    #     'field_name': 'number_of_spectral_points_in_retrieval',
                    #     'flag': False,
                    #     'log_range': False,
                    #     'primary_variable': 'number_of_spectral_points_in_retrieval',
                    #     'show': True,
                    #     'include_scatter': False,
                    #     'title': 'Number of spectral points',
                    #     'units': ''
                    # },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-0.1, 0.1],
                        'field_name': 'calibration_subwindows_shift',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'calibration_subwindows_shift',
                        'show': True,
                        'title': 'Wavelength calibration subwindows shift',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-0.1, 0.1],
                        'field_name': 'calibration_subwindows_squeeze',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'calibration_subwindows_squeeze',
                        'show': True,
                        'title': 'Wavelength calibration subwindows squeeze',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-0.1, 0.1],
                        'field_name': 'calibration_polynomial_coefficients',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'calibration_polynomial_coefficients',
                        'show': True,
                        'title': 'Wavelength calibration polynomial coefficients',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-0.1, 0.1],
                        'field_name': 'calibration_subwindows_root_mean_square',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'calibration_subwindows_root_mean_square',
                        'show': True,
                        'title': 'Wavelength calibration subwindows RMS',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-0.1, 0.1],
                        'field_name': 'calibration_subwindows_shift_first_interval',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'calibration_subwindows_shift_first_interval',
                        'show': True,
                        'title': 'Wavelength calibration shift first interval',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-0.1, 0.1],
                        'field_name': 'calibration_subwindows_squeeze_first_interval',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'calibration_subwindows_squeeze_first_interval',
                        'show': True,
                        'title': 'Wavelength calibration squeeze first interval',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-0.1, 0.1],
                        'field_name': 'calibration_polynomial_coefficients_first_interval',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'calibration_polynomial_coefficients_first_interval',
                        'show': True,
                        'title': 'Wavelength calibration polynomial first interval',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-0.1, 0.1],
                        'field_name': 'calibration_subwindows_rms_first_interval',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'calibration_subwindows_rms_first_interval',
                        'show': True,
                        'title': 'Wavelength calibration RMS first interval',
                        'units': ''
                    },
                    # {
                    #    'color_scale': 'nipy_spectral',
                    #    'data_range': [200,300],
                    #    'field_name': 'number_of_spectral_points_in_retrieval_win1',
                    #    'flag': False,
                    #    'log_range': False,
                    #    'primary_variable': 'number_of_spectral_points_in_retrieval_win1',
                    #    'show': True,
                    #    'include_scatter': False,
                    #    'title': 'Number of spectral points in first interval',
                    #    'units': ''
                    # },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [-2E-3, 2E-3],
                        'field_name': 'formaldehyde_slant_column_corrected',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'formaldehyde_slant_column_corrected',
                        'show': False,
                        'title': 'HCHO slant column corrected',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 5E-4],
                        'field_name': 'formaldehyde_slant_column_correction',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'formaldehyde_slant_column_corrected - formaldehyde_slant_column_density',
                        'show': True,
                        'title': 'HCHO slant column correction',
                        'units': 'mol m\u207B\u00B2'
                    }
                ]
        },
        'NO2___': {
            'contact': 'Henk Eskes',
            'contact_email': 'henk.eskes@knmi.nl',
            'alternate_contact': 'Jos van Geffen',
            'alternate_contact_email': 'jos.van.geffen@knmi.nl',
            'developer': 'KNMI',
            'developer_contact': 'tropomi_l2_dev@knmi.nl',
            'variables':
                [
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [2.0e-07, 2.0e-4],
                        'field_name': 'nitrogendioxide_tropospheric_column',
                        'flag': False,
                        'log_range': True,
                        'primary_variable': 'nitrogendioxide_tropospheric_column',
                        'show': True,
                        'title': 'NO\u2082 tropospheric vertical column',
                        'units': 'mol m\u207B\u00B2'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [1.0e-06, 1e-4],
                        'field_name': 'nitrogendioxide_tropospheric_column_precision',
                        'flag': False,
                        'log_range': True,
                        'level3': False,
                        'primary_variable': 'nitrogendioxide_tropospheric_column_precision',
                        'show': True,
                        'title': 'NO\u2082 tropospheric vertical column precision',
                        'units': 'mol m\u207B\u00B2'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 12.0],
                        'field_name': 'air_mass_factor_troposphere',
                        'flag': False,
                        'log_range': False,
                        'level3': False,
                        'primary_variable': 'air_mass_factor_troposphere',
                        'show': True,
                        'title': 'Tropospheric airmass factor',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 12.0],
                        'field_name': 'air_mass_factor_total',
                        'flag': False,
                        'log_range': False,
                        'level3': False,
                        'primary_variable': 'air_mass_factor_total',
                        'show': True,
                        'title': 'Total airmass factor',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [270, 310],
                        'histogram_bincount': 41,
                        'level3': False,
                        'field_name': 'number_of_spectral_points_in_retrieval',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'number_of_spectral_points_in_retrieval',
                        'show': True,
                        'include_scatter': False,
                        'title': 'Number of spectral points in retrieval',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 15],
                        'field_name': 'number_of_iterations',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'number_of_iterations',
                        'histogram_bincount': 16,
                        'show': True,
                        'include_scatter': False,
                        'title': 'Number of iterations',
                        'units': '1',
                        'level3': False,
                    },
                    {
                        'color_scale': 'seismic',
                        'data_range': [-0.08, 0.08],
                        'field_name': 'wavelength_calibration_offset',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_offset',
                        'show': True,
                        'title': 'Wavelength calibration offset',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 0.001],
                        'field_name': 'wavelength_calibration_offset_precision',
                        'flag': False,
                        'log_range': False,
                        'level3': False,
                        'primary_variable': 'wavelength_calibration_offset_precision',
                        'show': True,
                        'title': 'Wavelength calibration offset precision',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [2.0e2, 1.0e5],
                        'field_name': 'wavelength_calibration_chi_square',
                        'flag': False,
                        'log_range': True,
                        'primary_variable': 'wavelength_calibration_chi_square',
                        'show': True,
                        'level3': False,
                        'title': 'Wavelength calibration \u03C7\u00B2',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 0.0001],
                        'field_name': 'nitrogendioxide_stratospheric_column',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'nitrogendioxide_stratospheric_column',
                        'show': True,
                        'title': 'Stratospheric vertical NO\u2082 column',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 1e-5],
                        'field_name': 'nitrogendioxide_stratospheric_column_precision',
                        'flag': False,
                        'level3': False,
                        'log_range': False,
                        'primary_variable': 'nitrogendioxide_stratospheric_column_precision',
                        'show': True,
                        'title': 'Stratospheric vertical NO\u2082 column precision',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [5.0e-06, 5.0e-4],
                        'field_name': 'nitrogendioxide_total_column',
                        'flag': False,
                        'log_range': True,
                        'primary_variable': 'nitrogendioxide_total_column',
                        'show': True,
                        'title': 'Total vertical NO\u2082 column',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [1e-6, 1e-4],
                        'field_name': 'nitrogendioxide_total_column_precision',
                        'level3': False,
                        'flag': False,
                        'log_range': True,
                        'primary_variable': 'nitrogendioxide_total_column_precision',
                        'show': True,
                        'title': 'Total vertical NO\u2082 column precision',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [5.0e-6, 5.0e-4],
                        'field_name': 'nitrogendioxide_summed_total_column',
                        'flag': False,
                        'log_range': True,
                        'primary_variable': 'nitrogendioxide_summed_total_column',
                        'show': True,
                        'title': 'Summed vertical NO\u2082 column',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [1e-6, 1e-4],
                        'level3': False,
                        'field_name': 'nitrogendioxide_summed_total_column_precision',
                        'flag': False,
                        'log_range': True,
                        'primary_variable': 'nitrogendioxide_summed_total_column_precision',
                        'show': True,
                        'title': 'Summed vertical NO\u2082 column precision',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 2500],
                        'field_name': 'chi_square',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'chi_square',
                        'show': True,
                        'title': '\u03C7\u00B2',
                        'level3': False,
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [1.0e-5, 1e-3],
                        'field_name': 'root_mean_square_error_of_fit',
                        'flag': False,
                        'log_range': True,
                        'primary_variable': 'root_mean_square_error_of_fit',
                        'show': True,
                        'title': 'RMS',
                        'level3': False,
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 12],
                        'field_name': 'air_mass_factor_stratosphere',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'air_mass_factor_stratosphere',
                        'show': True,
                        'level3': False,
                        'title': 'Stratospheric airmass factor',
                        'units': ''
                    },
                    {
                        'color_scale': 'seismic',
                        'data_range': [-0.1, 0.1],
                        'field_name': 'wavelength_calibration_irradiance_offset',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_irradiance_offset',
                        'show': True,
                        'title': 'Spectral offset irradiance (\u03BB(true) \u2212 \u03BB(nominal))',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 0.1],
                        'field_name': 'wavelength_calibration_irradiance_offset_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_irradiance_offset_precision',
                        'show': True,
                        'title': 'Precision of spectral offset irradiance (\u03BB(true) \u2212 \u03BB(nominal))',
                        'units': 'nm'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0.0, 100.0],
                        'field_name': 'wavelength_calibration_irradiance_chi_square',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'wavelength_calibration_irradiance_chi_square',
                        'show': True,
                        'title': '\u03C7\u00B2 of irradiance wavelength calibration',
                        'units': ''
                    }
                ]
        },
        'NP_BD6': {
            'contact': 'Richard Siddans',
            'contact_email': 'richard.siddans@stfc.ac.uk',
            'developer': 'RAL',
            'developer_contact': 'richard.siddans@stfc.ac.uk',
            'variables':
                [
                    {
                        'color_scale': 'viridis',
                        'data_range': [-350, -150],
                        'field_name': 'viirs_delta_time',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'viirs_delta_time',
                        'show': True,
                        'title': '$\Delta$ time',
                        'units': 's'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 80],
                        'field_name': 'viirs_viewing_zenith_angle',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'viirs_viewing_zenith_angle',
                        'show': True,
                        'title': 'VIIRS viewing zenith angle',
                        'units': '\u00B0'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 600],
                        'field_name': 'vcm_confidently_cloudy',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'vcm_confidently_cloudy',
                        'show': False,
                        'internal_only': True,
                        'title': 'VIIRS cloud mask confidently cloud',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 0, 'collapse': False}
                                }
                            ],
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0, 600],
                        'field_name': 'vcm_probably_cloudy',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'vcm_probably_cloudy',
                        'show': False,
                        'internal_only': True,
                        'title': 'VIIRS cloud mask probably cloudy',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 0, 'collapse': False}
                                }
                            ],
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0, 600],
                        'field_name': 'vcm_probably_clear',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'vcm_probably_clear',
                        'show': False,
                        'internal_only': True,
                        'title': 'VIIRS cloud mask probably clear',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 0, 'collapse': False}
                                }
                            ],
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0, 600],
                        'field_name': 'vcm_confidently_clear',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'vcm_confidently_clear',
                        'show': False,
                        'internal_only': True,
                        'title': 'VIIRS cloud mask confidently clear',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 0, 'collapse': False}
                                }
                            ],
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0, 600],
                        'field_name': 'vcm_nvalid',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'vcm_confidently_cloudy+vcm_probably_cloudy+vcm_probably_clear+vcm_confidently_clear',
                        'show': True,
                        'title': 'VIIRS cloud mask valid input',
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.0, 1.0],
                        'field_name': 'vcm_confidently_cloudy_fraction',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'vcm_confidently_cloudy/vcm_nvalid',
                        'show': True,
                        'title': 'VIIRS cloud mask confidently cloud',
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.0, 1.0],
                        'field_name': 'vcm_probably_cloudy_fraction',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'vcm_probably_cloudy/vcm_nvalid',
                        'show': True,
                        'title': 'VIIRS cloud mask probably cloudy',
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.0, 1.0],
                        'field_name': 'vcm_probably_clear_fraction',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'vcm_probably_clear/vcm_nvalid',
                        'show': True,
                        'title': 'VIIRS cloud mask probably clear',
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.0, 1.0],
                        'field_name': 'vcm_confidently_clear_fraction',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'vcm_confidently_clear/vcm_nvalid',
                        'show': True,
                        'title': 'VIIRS cloud mask confidently clear',
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.0, 1.0],
                        'field_name': 'band07_srf_mean',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'band07_srf_mean',
                        'show': True,
                        'title': 'Mean of valid VIIRS band M07 reflectance',
                        'transformers':
                            [
                                {
                                    'class': 'transform.SunNormalizedRadiance',
                                    'arguments': {}
                                }
                            ],
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.0, 1.0],
                        'field_name': 'band09_srf_mean',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'band09_srf_mean',
                        'show': True,
                        'title': 'Mean of valid VIIRS band M09 reflectance',
                        'transformers':
                            [
                                {
                                    'class': 'transform.SunNormalizedRadiance',
                                    'arguments': {}
                                }
                            ],
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.0, 1.0],
                        'field_name': 'band11_srf_mean',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'band11_srf_mean',
                        'show': True,
                        'title': 'Mean of valid VIIRS band M11 reflectance',
                        'transformers':
                            [
                                {
                                    'class': 'transform.SunNormalizedRadiance',
                                    'arguments': {}
                                }
                            ],
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.0, 1.0],
                        'field_name': 'band07_fov_mean',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'band07_fov_mean',
                        'show': True,
                        'title': 'Mean of valid VIIRS band M07 reflectance in FOV',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 0, 'collapse': False}
                                },
                                {
                                    'class': 'transform.SunNormalizedRadiance',
                                    'arguments': {}
                                }
                            ],
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.0, 0.75],
                        'field_name': 'band09_fov_mean',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'band09_fov_mean',
                        'show': True,
                        'title': 'Mean of valid VIIRS band M09 reflectance in FOV',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 0, 'collapse': False}
                                },
                                {
                                    'class': 'transform.SunNormalizedRadiance',
                                    'arguments': {}
                                }
                            ],
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.0, 0.5],
                        'field_name': 'band11_fov_mean',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'band11_fov_mean',
                        'show': True,
                        'title': 'Mean of valid VIIRS band M11 reflectance in FOV',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 0, 'collapse': False}
                                },
                                {
                                    'class': 'transform.SunNormalizedRadiance',
                                    'arguments': {}
                                }
                            ],
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.0, 0.4],
                        'field_name': 'band07_fov_stdev',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'band07_fov_stdev',
                        'show': True,
                        'title': 'Standard deviation of valid VIIRS band M07 reflectance in FOV',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 0, 'collapse': False}
                                },
                                {
                                    'class': 'transform.SunNormalizedRadiance',
                                    'arguments': {}
                                }
                            ],
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.0, 0.25],
                        'field_name': 'band09_fov_stdev',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'band09_fov_stdev',
                        'show': True,
                        'title': 'Standard deviation of valid VIIRS band M09 reflectance in FOV',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 0, 'collapse': False}
                                },
                                {
                                    'class': 'transform.SunNormalizedRadiance',
                                    'arguments': {}
                                }
                            ],
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.0, 0.25],
                        'field_name': 'band11_fov_stdev',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'band11_fov_stdev',
                        'show': True,
                        'title': 'Standard deviation of valid VIIRS band M11 reflectance in FOV',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 0, 'collapse': False}
                                },
                                {
                                    'class': 'transform.SunNormalizedRadiance',
                                    'arguments': {}
                                }
                            ],
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0, 600],
                        'field_name': 'band07_fov_nvalid',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'band07_fov_nvalid',
                        'show': True,
                        'title': 'Number of valid VIIRS band M07 pixels in FOV',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 0, 'collapse': False}
                                }
                            ],
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0, 600],
                        'field_name': 'band09_fov_nvalid',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'band09_fov_nvalid',
                        'show': True,
                        'title': 'Number of valid VIIRS band M09 pixels in FOV',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 0, 'collapse': False}
                                }
                            ],
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0, 600],
                        'field_name': 'band11_fov_nvalid',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'band11_fov_nvalid',
                        'show': True,
                        'title': 'Number of valid VIIRS band M11 pixels in FOV',
                        'transformers':
                            [
                                {
                                    'class': 'transform.Select',
                                    'arguments': {'dimension': -1, 'index': 0, 'collapse': False}
                                }
                            ],
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.95, 1.0],
                        'field_name': 'band07_srf_coverage',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'band07_srf_coverage',
                        'show': True,
                        'title': 'Fractional energy of SRF covered by valid VIIRS band M07 radiances',
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.95, 1.0],
                        'field_name': 'band09_srf_coverage',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'band09_srf_coverage',
                        'show': True,
                        'title': 'Fractional energy of SRF covered by valid VIIRS band M09 radiances',
                        'units': ''
                    },
                    {
                        'color_scale': 'viridis',
                        'data_range': [0.95, 1.0],
                        'field_name': 'band11_srf_coverage',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'band11_srf_coverage',
                        'show': True,
                        'title': 'Fractional energy of SRF covered by valid VIIRS band M11 radiances',
                        'units': ''
                    }
                ]
        },
        'NP_BD7': {
            'equivalent_product': 'NP_BD6'
        },
        'NP_BD3': {
            'equivalent_product': 'NP_BD6'
        },
        'O3_TCL': {
            'contact': 'Klaus-Peter Heue',
            'contact_email': 'Klaus-peter.heue@dlr.de',
            'developer': 'DLR',
            'developer_contact': 'mattia.pedergnana@dlr.de',
            'do_not_process': True,
            'actions': [],
            'variables': []
        },
        'O3_TPR': {
            'contact': 'Johan de Haan',
            'contact_email': 'johan.de.haan@knmi.nl',
            'developer': 'KNMI',
            'developer_contact': 'tropomi_l2_dev@knmi.nl',
            'variables':
                [
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 10],
                        'field_name': 'number_of_iterations',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'number_of_iterations',
                        'histogram_bincount': 11,
                        'show': True,
                        'level3': False,
                        'title': 'Number of iterations',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [21, 120],
                        'field_name': 'number_of_spectral_points_in_retrieval',
                        'histogram_bincount': 100,
                        'flag': False,
                        'log_range': False,
                        'level3': False,
                        'primary_variable': 'number_of_spectral_points_in_retrieval',
                        'show': True,
                        'title': 'Number of spectral points in retrieval',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 2],
                        'field_name': 'ozone_tropospheric_column',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'ozone_tropospheric_column',
                        'show': True,
                        'title': 'O\u2083 tropospheric column',
                        'units': 'mol m\u207B\u00B2'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 1],
                        'field_name': 'ozone_tropospheric_column_precision',
                        'flag': False,
                        'log_range': False,
                        'level3': False,
                        'primary_variable': 'ozone_tropospheric_column_precision',
                        'show': True,
                        'title': 'Precision of the O\u2083 tropospheric column',
                        'units': 'mol m\u207B\u00B2'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 100],
                        'field_name': 'root_mean_square_error_of_fit',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'root_mean_square_error_of_fit',
                        'show': True,
                        'level3': False,
                        'title': 'RMS',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 10],
                        'field_name': 'degrees_of_freedom',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'degrees_of_freedom',
                        'level3': False,
                        'show': True,
                        'title': 'Total degrees of freedom',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 3],
                        'field_name': 'degrees_of_freedom_ozone',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'degrees_of_freedom_ozone',
                        'show': True,
                        'title': 'Degrees of freedom for O\u2083',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 3],
                        'level3': False,
                        'field_name': 'cost_function',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cost_function',
                        'show': True,
                        'title': 'Cost function',
                        'units': ''
                    }
                ]
        },
        'O3__PR': {
            'contact': 'Johan de Haan',
            'contact_email': 'johan.de.haan@knmi.nl',
            'developer': 'KNMI',
            'developer_contact': 'tropomi_l2_dev@knmi.nl',
            'variables':
                [
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 10],
                        'field_name': 'number_of_iterations',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'number_of_iterations',
                        'histogram_bincount': 11,
                        'level3': False,
                        'show': True,
                        'title': 'Number of iterations',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [91, 190],
                        'level3': False,
                        'field_name': 'number_of_spectral_points_in_retrieval',
                        'histogram_bincount': 100,
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'number_of_spectral_points_in_retrieval',
                        'show': True,
                        'title': 'Number of spectral points in retrieval',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 2],
                        'field_name': 'ozone_total_column',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'ozone_total_column',
                        'show': True,
                        'title': 'O\u2083 total column',
                        'units': 'mol m\u207B\u00B2'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 1],
                        'level3': False,
                        'field_name': 'ozone_total_column_precision',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'ozone_total_column_precision',
                        'show': True,
                        'title': 'Precision of the O\u2083 total column',
                        'units': 'mol m\u207B\u00B2'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 2],
                        'field_name': 'ozone_tropospheric_column',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'ozone_tropospheric_column',
                        'show': True,
                        'title': 'O\u2083 tropospheric column',
                        'units': 'mol m\u207B\u00B2'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 1],
                        'field_name': 'ozone_tropospheric_column_precision',
                        'level3': False,
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'ozone_tropospheric_column_precision',
                        'show': True,
                        'title': 'Precision of the O\u2083 tropospheric column',
                        'units': 'mol m\u207B\u00B2'
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 100],
                        'field_name': 'root_mean_square_error_of_fit',
                        'flag': False,
                        'level3': False,
                        'log_range': False,
                        'primary_variable': 'root_mean_square_error_of_fit',
                        'show': True,
                        'title': 'RMS',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 10],
                        'field_name': 'degrees_of_freedom',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'degrees_of_freedom',
                        'level3': False,
                        'show': True,
                        'title': 'Total degrees of freedom',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 3],
                        'field_name': 'degrees_of_freedom_ozone',
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'degrees_of_freedom_ozone',
                        'show': True,
                        'title': 'Degrees of freedom for O\u2083',
                        'units': ''
                    },
                    {
                        'color_scale': 'nipy_spectral',
                        'data_range': [0, 3],
                        'field_name': 'cost_function',
                        'level3': False,
                        'flag': False,
                        'log_range': False,
                        'primary_variable': 'cost_function',
                        'show': True,
                        'title': 'Cost function',
                        'units': ''
                    }
                ]
        },
        'O3____': {
            'contact': 'Klaus-Peter Heue',
            'contact_email': 'klaus-peter.heue@dlr.de',
            'developer': 'DLR',
            'developer_contact': 'mattia.pedergnana@dlr.de',
            'variables': [
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [0, 0.3],
                    'field_name': 'ozone_total_vertical_column',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'ozone_total_vertical_column',
                    'show': True,
                    'title': 'O\u2083 vertical column',
                    'units': 'mol m\u207B\u00B2',
                    'transformers':
                        [
                            {
                                'class': 'transform.ThresholdFilter',
                                'arguments': {'threshold': 10, 'comparison': ">"}
                            }
                        ]
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [0, 0.03],
                    'field_name': 'ozone_total_vertical_column_precision',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'ozone_total_vertical_column_precision',
                    'show': True,
                    'title': 'O\u2083 vertical column precision',
                    'units': 'mol m\u207B\u00B2',
                    'transformers':
                        [
                            {
                                'class': 'transform.ThresholdFilter',
                                'arguments': {'threshold': 10, 'comparison': ">"}
                            }
                        ]
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [0, 1],
                    'field_name': 'ozone_slant_column_density',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'fitted_slant_columns',
                    'show': True,
                    'title': 'O\u2083 slant column',
                    'units': 'mol m\u207B\u00B2',
                    'transformers':
                        [
                            {
                                'class': 'transform.Select',
                                'arguments': {'dimension': -1, 'index': 0}
                            },
                            {
                                'class': 'transform.ThresholdFilter',
                                'arguments': {'threshold': 20, 'comparison': ">"}
                            }
                        ],
                    'modes': ['NRTI']
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [0, 7E-3],
                    'field_name': 'ozone_slant_column_precision',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'fitted_slant_columns_precision',
                    'show': True,
                    'title': 'O\u2083 slant column precision',
                    'units': 'mol m\u207B\u00B2',
                    'transformers':
                        [
                            {
                                'class': 'transform.Select',
                                'arguments': {'dimension': -1, 'index': 0}
                            },
                            {
                                'class': 'transform.ThresholdFilter',
                                'arguments': {'threshold': 20, 'comparison': ">"}
                            }
                        ],
                    'modes': ['NRTI']
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [0, 6],
                    'field_name': 'number_of_iterations_slant_column',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'number_of_iterations_slant_column',
                    'histogram_bincount': 21,
                    'show': True,
                    'include_scatter': False,
                    'Level3': False,
                    'title': 'Number of iterations for slant column retrieval',
                    'units': '',
                    'modes': ['NRTI']
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [0, 0.01],
                    'field_name': 'root_mean_square_slant_column_fit',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'fitted_root_mean_square',
                    'show': True,
                    'include_scatter': False,
                    'title': 'Fitting RMS',
                    'units': ''
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [-0.05, 0.05],
                    'field_name': 'fitted_radiance_shift',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'fitted_radiance_shift',
                    'show': True,
                    'title': 'DOAS fit wavelength shift',
                    'units': 'nm',
                    'modes': ['NRTI']
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [-0.03, 0.03],
                    'field_name': 'fitted_radiance_squeeze',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'fitted_radiance_squeeze',
                    'show': True,
                    'title': 'DOAS fit wavelength squeeze',
                    'units': '',
                    'modes': ['NRTI']
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [0, 10],
                    'field_name': 'ozone_total_air_mass_factor',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'ozone_total_air_mass_factor',
                    'show': True,
                    'title': 'Airmass factor',
                    'units': '',
                    'modes': ['NRTI']
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [0, 0.05],
                    'field_name': 'ozone_total_air_mass_factor_trueness',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'ozone_total_air_mass_factor_trueness',
                    'show': True,
                    'title': 'Airmass factor trueness',
                    'units': '',
                    'modes': ['NRTI']
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [200, 250],
                    'field_name': 'ozone_effective_temperature',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'ozone_effective_temperature',
                    'show': True,
                    'title': 'Effective temperature',
                    'units': 'K'
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [0, 0.02],
                    'field_name': 'ozone_ghost_column',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'ozone_ghost_column',
                    'show': True,
                    'title': 'O\u2083 ghost column',
                    'units': 'mol m\u207B\u00B2',
                    'modes': ['OFFL', 'RPRO']
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [0, 3],
                    'field_name': 'intra_cloud_correction_factor',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'intra_cloud_correction_factor',
                    'show': True,
                    'title': 'intra-cloud correction factor',
                    'units': '',
                    'modes': ['OFFL', 'RPRO']
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [0, 10],
                    'field_name': 'number_of_iterations_vertical_column',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'number_of_iterations_vertical_column',
                    'histogram_bincount': 21,
                    'show': True,
                    'include_scatter': False,
                    'Level3': False,
                    'title': 'Number of iterations for vertical column retrieval',
                    'units': ''
                },
                # {
                #     'color_scale': 'nipy_spectral',
                #     'data_range': [70,90],
                #     'histogram_bincount': 21,
                #      'field_name': 'number_of_spectral_points_in_retrieval',
                #      'flag': False,
                #      'log_range': False,
                #      'primary_variable': 'number_of_spectral_points_in_retrieval',
                #      'show': True,
                #      'title': 'Number of spectral points in retrieval',
                #      'units': ''
                #  },
                # {
                # 'color_scale': 'nipy_spectral',
                # 'data_range': [0,400],
                # 'field_name': 'vcd_root_mean_square',
                # 'flag': False,
                # 'log_range': False,
                # 'primary_variable': 'vcd_root_mean_square',
                # 'show': True,
                # 'title': 'Vertical column RMS',
                # 'units': ''
                # },
                # # {
                # # 'color_scale': 'nipy_spectral',
                # # 'data_range': [21,120],
                # # 'field_name': 'vcd_chi_square',
                # # 'flag': False,
                # # 'log_range': False,
                # # 'primary_variable': 'vcd_chi_square',
                # # 'show': True,
                # # 'title': 'Vertical column \u03C7\u00B2',
                # # 'units': ''
                # # },
                # {
                # 'color_scale': 'nipy_spectral',
                # 'data_range': [0,10],
                # 'field_name': 'degrees_of_freedom',
                # 'flag': False,
                # 'log_range': False,
                # 'primary_variable': 'degrees_of_freedom',
                # 'show': True,
                # 'title': 'Degrees of freedom',
                # 'units': ''
                # },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [-0.05, 0.05],
                    'field_name': 'calibration_subwindows_shift',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'calibration_subwindows_shift',
                    'show': True,
                    'title': 'Wavelength calibration subwindows shift',
                    'units': 'nm'
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [-0.05, 0.05],
                    'field_name': 'calibration_subwindows_squeeze',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'calibration_subwindows_squeeze',
                    'show': True,
                    'title': 'Wavelength calibration subwindows squeeze',
                    'units': ''
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [-0.05, 0.05],
                    'field_name': 'calibration_polynomial_coefficients',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'calibration_polynomial_coefficients',
                    'show': True,
                    'title': 'Wavelength calibration polynomial coefficients',
                    'units': ''
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [0, 400],
                    'field_name': 'calibration_subwindows_root_mean_square',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'calibration_subwindows_root_mean_square',
                    'show': True,
                    'title': 'Wavelength calibration subwindows RMS',
                    'units': ''
                }
            ]
        },
        'SO2___': {
            'contact': 'Nicolas Theys',
            'contact_email': 'nicolas.theys@aeronomie.be',
            'developer': 'DLR',
            'developer_contact': 'mattia.pedergnana@dlr.de',
            'variables': [
                {
                    'color_scale': 'jet',
                    'data_range': [0.1, 25],
                    # 'data_range': [1E-4,1e-2],
                    'field_name': 'sulfurdioxide_total_vertical_column',
                    'flag': False,
                    'log_range': True,
                    'primary_variable': 'sulfurdioxide_total_vertical_column',
                    'show': True,
                    'title': 'SO\u2082 vertical column',
                    'transformers':
                        [
                            {
                                'class': 'transform.Multiplier',
                                'arguments': {'operator': '*', 'scalefactor': 2241.15}
                            },
                        ],
                    'units': 'DU',
                    # 'units': 'mol m\u207B\u00B2',

                },
                {
                    'color_scale': 'jet',
                    'data_range': [0.1, 25],
                    # 'data_range': [1E-4,1e-2],
                    'field_name': 'sulfurdioxide_total_vertical_column_1km',
                    'flag': False,
                    'log_range': True,
                    'primary_variable': 'sulfurdioxide_total_vertical_column_1km',
                    'show': True,
                    'title': 'SO\u2082 vertical column 1 km',
                    'transformers':
                        [
                            {
                                'class': 'transform.Multiplier',
                                'arguments': {'operator': '*', 'scalefactor': 2241.15}
                            },
                        ],
                    'units': 'DU',
                    # 'units': 'mol m\u207B\u00B2',
                    'modes': ['NRTI']
                },
                {
                    'color_scale': 'jet',
                    'data_range': [0.1, 25],
                    # 'data_range': [1E-4,1e-2],
                    'field_name': 'sulfurdioxide_total_vertical_column_7km',
                    'flag': False,
                    'log_range': True,
                    'primary_variable': 'sulfurdioxide_total_vertical_column_7km',
                    'show': True,
                    'title': 'SO\u2082 vertical column 7 km',
                    'transformers':
                        [
                            {
                                'class': 'transform.Multiplier',
                                'arguments': {'operator': '*', 'scalefactor': 2241.15}
                            },
                        ],
                    'units': 'DU',
                    # 'units': 'mol m\u207B\u00B2',
                    'modes': ['NRTI']
                },
                {
                    'color_scale': 'jet',
                    'data_range': [0.1, 25],
                    # 'data_range': [1E-4,1e-2],
                    'field_name': 'sulfurdioxide_total_vertical_column_15km',
                    'flag': False,
                    'log_range': True,
                    'primary_variable': 'sulfurdioxide_total_vertical_column_15km',
                    'show': True,
                    'title': 'SO\u2082 vertical column 15 km',
                    'transformers':
                        [
                            {
                                'class': 'transform.Multiplier',
                                'arguments': {'operator': '*', 'scalefactor': 2241.15}
                            },
                        ],
                    'units': 'DU',
                    # 'units': 'mol m\u207B\u00B2',
                    'modes': ['NRTI']
                },
                {
                    'color_scale': 'Reds',
                    'data_range': [0.01, 2.5],
                    # 'data_range': [0,0.003],
                    'field_name': 'sulfurdioxide_total_vertical_column_precision',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'sulfurdioxide_total_vertical_column_precision',
                    'show': True,
                    'title': 'SO\u2082 vertical column precision',
                    'transformers':
                        [
                            {
                                'class': 'transform.Multiplier',
                                'arguments': {'operator': '*', 'scalefactor': 2241.15}
                            },
                        ],
                    'units': 'DU'
                    # 'units': 'mol m\u207B\u00B2',
                },
                {
                    'color_scale': 'jet',
                    'data_range': [0.1, 2.5],
                    # 'data_range': [-1E-3,1E-3],
                    'field_name': 'sulfurdioxide_slant_column_density_corrected',
                    'flag': False,
                    'log_range': True,
                    'primary_variable': 'sulfurdioxide_slant_column_corrected',
                    'show': True,
                    'title': 'Corrected SO\u2082 slant column',
                    'transformers':
                        [
                            {
                                'class': 'transform.Multiplier',
                                'arguments': {'operator': '*', 'scalefactor': 2241.15}
                            },
                        ],
                    'units': 'DU'
                    # 'units': 'mol m\u207B\u00B2',
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [1, 3],
                    'field_name': 'selected_fitting_window_flag',
                    'flag': True,
                    'log_range': False,
                    'primary_variable': 'selected_fitting_window_flag',
                    'show': True,
                    'title': 'slant column window flag',
                    'units': ''
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-2.5, 2.5],
                    # 'data_range': [-1E-3,1E-3],
                    'field_name': 'sulfurdioxide_slant_column_density_window1',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'fitted_slant_columns_win1',
                    'show': True,
                    'title': 'SO\u2082 slant column (window 1)',
                    'transformers':
                        [
                            {
                                'class': 'transform.Select',
                                'arguments': {'dimension': -1, 'index': 0}
                            },
                            {
                                'class': 'transform.Multiplier',
                                'arguments': {'operator': '*', 'scalefactor': 2241.15}
                            },
                        ],
                    'units': 'DU',
                    # 'units': 'mol m\u207B\u00B2',
                },
                {
                    'color_scale': 'Reds',
                    'data_range': [0., 2.5],
                    'field_name': 'sulfurdioxide_slant_column_density_window1_precision',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'fitted_slant_columns_win1_precision',
                    'show': True,
                    'title': 'SO\u2082 slant column precision (window 1)',
                    'transformers':
                        [
                            {
                                'class': 'transform.Select',
                                'arguments': {'dimension': -1, 'index': 0}
                            },
                            {
                                'class': 'transform.Multiplier',
                                'arguments': {'operator': '*', 'scalefactor': 2241.15}
                            },
                        ],
                    'units': 'DU',
                    # 'units': 'mol m\u207B\u00B2',
                },
                #                    {
                #                        'color_scale': 'nipy_spectral',
                #                        'data_range': [0,400],
                #                        'field_name': 'background_so2_slant_column_offset',
                #                        'flag': False,
                #                        'log_range': False,
                #                        'primary_variable': 'sulfurdioxide_slant_column_density_corrected - sulfurdioxide_slant_column_density_window1',
                #                        'show': True,
                #                        'title': 'Background corrected SO\u2082 slant column offset',
                #                        'units': 'mol m\u207B\u00B2'
                #                    },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-2.5, 2.5],
                    # 'data_range': [-1E-3,1E-3],
                    'field_name': 'sulfurdioxide_slant_column_density_corrected_win1',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'sulfurdioxide_slant_column_corrected_win1',
                    'show': True,
                    'internal_only': True,
                    'title': 'Corrected SO\u2082 slant column (window 1)',
                    'transformers':
                        [
                            {
                                'class': 'transform.Multiplier',
                                'arguments': {'operator': '*', 'scalefactor': 2241.15}
                            },
                        ],
                    'units': 'DU'
                    # 'units': 'mol m\u207B\u00B2',
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-2, 2],
                    'field_name': 'background_so2_slant_column_offset_window1',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'sulfurdioxide_slant_column_density_corrected_win1 - sulfurdioxide_slant_column_density_window1',
                    'show': True,
                    'title': 'SO\u2082 slant column background correction (window 1)',
                    'units': 'DU'
                    # 'units': 'mol m\u207B\u00B2',
                },
                {
                    'color_scale': 'jet',
                    'data_range': [-25, 25],
                    # 'data_range': [-1E-3,1E-3],
                    'field_name': 'sulfurdioxide_slant_column_density_window2',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'fitted_slant_columns_win2',
                    'show': True,
                    'internal_only': True,
                    'title': 'SO\u2082 slant column (window 2)',
                    'transformers':
                        [
                            {
                                'class': 'transform.Select',
                                'arguments': {'dimension': -1, 'index': 0}
                            },
                            {
                                'class': 'transform.Multiplier',
                                'arguments': {'operator': '*', 'scalefactor': 2241.15}
                            },
                        ],
                    'units': 'DU',
                    # 'units': 'mol m\u207B\u00B2',
                },
                {
                    'color_scale': 'Reds',
                    'data_range': [0, 45],
                    # 'data_range': [0,0.02],
                    'field_name': 'sulfurdioxide_slant_column_density_window2_precision',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'fitted_slant_columns_win2_precision',
                    'show': True,
                    'title': 'SO\u2082 slant column precision (window2)',
                    'transformers':
                        [
                            {
                                'class': 'transform.Select',
                                'arguments': {'dimension': -1, 'index': 0}
                            },
                            {
                                'class': 'transform.Multiplier',
                                'arguments': {'operator': '*', 'scalefactor': 2241.15}
                            },
                        ],
                    'units': 'DU',
                    # 'units': 'mol m\u207B\u00B2',
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-25, 25],
                    # 'data_range': [-1E-3,1E-3],
                    'field_name': 'sulfurdioxide_slant_column_density_corrected_win2',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'sulfurdioxide_slant_column_corrected_win2',
                    'show': True,
                    'title': 'Corrected SO\u2082 slant column (window 2)',
                    'transformers':
                        [
                            {
                                'class': 'transform.Multiplier',
                                'arguments': {'operator': '*', 'scalefactor': 2241.15}
                            },
                        ],
                    'units': 'DU'
                    # 'units': 'mol m\u207B\u00B2',
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-25, 25],
                    'field_name': 'background_so2_slant_column_offset_window2',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'sulfurdioxide_slant_column_density_corrected_win2 - sulfurdioxide_slant_column_density_window2',
                    'show': True,
                    'title': 'SO\u2082 slant column background correction (window 2)',
                    'units': 'DU'
                },
                {
                    'color_scale': 'jet',
                    'data_range': [-56, 56],
                    'field_name': 'sulfurdioxide_slant_column_density_window3',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'fitted_slant_columns_win3',
                    'show': True,
                    'title': 'SO\u2082 slant column (window 3)',
                    'transformers':
                        [
                            {
                                'class': 'transform.Select',
                                'arguments': {'dimension': -1, 'index': 0}
                            },
                            {
                                'class': 'transform.Multiplier',
                                'arguments': {'operator': '*', 'scalefactor': 2241.15}
                            },
                        ],
                    'units': 'DU',
                    # 'units': 'mol m\u207B\u00B2',
                },
                {
                    'color_scale': 'Reds',
                    # 'data_range': [0,0.05],
                    'data_range': [0, 110],
                    'field_name': 'sulfurdioxide_slant_column_density_window3_precision',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'fitted_slant_columns_win3_precision',
                    'show': True,
                    'title': 'SO\u2082 slant column precision (window 3)',
                    'units': 'DU',
                    'transformers':
                        [
                            {
                                'class': 'transform.Multiplier',
                                'arguments': {'operator': '*', 'scalefactor': 2241.15}
                            },
                            {
                                'class': 'transform.Select',
                                'arguments': {'dimension': -1, 'index': 0}
                            }
                        ]
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-56, 56],
                    # 'data_range': [-0.025,0.025],
                    'field_name': 'sulfurdioxide_slant_column_density_corrected_win3',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'sulfurdioxide_slant_column_corrected_win3',
                    'show': True,
                    'title': 'Corrected SO\u2082 slant column (window 3)',
                    'transformers':
                        [
                            {
                                'class': 'transform.Multiplier',
                                'arguments': {'operator': '*', 'scalefactor': 2241.15}
                            },
                        ],
                    'units': 'DU',
                    # 'units': 'mol m\u207B\u00B2',
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-56, 56],
                    'field_name': 'background_so2_slant_column_offset_window3',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'sulfurdioxide_slant_column_density_corrected_win3 - sulfurdioxide_slant_column_density_window3',
                    'show': True,
                    'title': 'SO\u2082 slant column background correction (window 3)',
                    'units': 'DU'
                },
                {
                    'color_scale': 'jet',
                    # 'data_range': [1E-4,1E-2],
                    'data_range': [0.01, 25],
                    'modes': ['NRTI'],
                    'field_name': 'integrated_so2_profile_apriori',
                    'flag': False,
                    'log_range': True,
                    'primary_variable': 'sulfurdioxide_profile_apriori',
                    'secondary_variable': 'surface_pressure',
                    'show': True,
                    'title': 'Integrated a priori SO\u2082 profile',
                    'transformers':
                        [
                            {
                                'class': 'transform.IntegratedColumn',
                                'arguments': {'dimension': -1,
                                              'coefficients_a': 'read_from_file("tm5_constant_a")',
                                              'coefficients_b': 'read_from_file("tm5_constant_b")'}
                            },
                            {
                                'class': 'transform.Multiplier',
                                'arguments': {'operator': '*', 'scalefactor': 2241.15}
                            },
                        ],
                    'units': 'DU'
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-0.05, 0.01],
                    'field_name': 'fitted_radiance_shift',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'fitted_radiance_shift',
                    'show': True,
                    'title': 'DOAS fit wavelength shift',
                    'units': 'nm'
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-0.001, 0.001],
                    'field_name': 'fitted_radiance_squeeze',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'fitted_radiance_squeeze',
                    'show': True,
                    'title': 'DOAS fit wavelength squeeze',
                    'units': ''
                },
                {
                    'color_scale': 'Reds',
                    'data_range': [0, 0.005],
                    'field_name': 'fitted_root_mean_square',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'fitted_root_mean_square',
                    'show': True,
                    'title': 'SO\u2082 RMS',
                    'units': ''
                },
                {
                    'color_scale': 'Blues',
                    'data_range': [0, 4],
                    'field_name': 'sulfurdioxide_total_air_mass_factor_polluted',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'sulfurdioxide_total_air_mass_factor_polluted',
                    'show': True,
                    'title': 'Total AMF (polluted)',
                    'units': ''
                },
                {
                    'color_scale': 'Reds',
                    'data_range': [0, 1],
                    'field_name': 'sulfurdioxide_total_air_mass_factor_polluted_precision',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'sulfurdioxide_total_air_mass_factor_polluted_precision',
                    'show': True,
                    'title': 'Precision of total AMF (polluted)',
                    'units': ''
                },
                {
                    'color_scale': 'Blues',
                    'data_range': [0, 4],
                    'field_name': 'amf_clear_polluted',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'amf_clear_polluted_precision',
                    'show': True,
                    'title': 'Clear-sky AMF (polluted)',
                    'units': ''
                },
                {
                    'color_scale': 'Reds',
                    'data_range': [0, 4],
                    'field_name': 'amf_cloud_polluted',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'amf_cloud_polluted',
                    'show': True,
                    'title': 'Precision of cloudy AMF (polluted)',
                    'units': ''
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [21, 120],
                    'field_name': 'number_of_spectral_points_in_retrieval',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'number_of_spectral_points_in_retrieval',
                    'show': True,
                    'include_scatter': False,
                    'Level3': False,
                    'title': 'Number of spectral points in retrieval',
                    'units': ''
                },
                {
                    'color_scale': 'nipy_spectral',
                    'data_range': [0, 20],
                    'field_name': 'number_of_iterations_in_retrieval',
                    'flag': False,
                    'log_range': False,
                    'histogram_bincount': 21,
                    'primary_variable': 'number_of_iterations_in_retrieval',
                    'show': True,
                    'include_scatter': False,
                    'Level3': False,
                    'title': 'Number of iterations',
                    'units': ''
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-0.005, 0.005],
                    'field_name': 'calibration_subwindows_shift_win1',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'calibration_subwindows_shift_win1',
                    'show': True,
                    'title': 'Wavelength calibration subwindows shift (window 1)',
                    'units': 'nm'
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-0.005, 0.005],
                    'field_name': 'calibration_subwindows_squeeze_win1',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'calibration_subwindows_squeeze_win1',
                    'show': True,
                    'title': 'Wavelength calibration subwindows squeeze (window 1)',
                    'units': ''
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-0.005, 0.005],
                    'field_name': 'calibration_polynomial_coefficients_win1',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'calibration_polynomial_coefficients_win1',
                    'show': True,
                    'title': 'Wavelength calibration polynomial coefficients (window 1)',
                    'units': ''
                },
                {
                    'color_scale': 'Blues',
                    'data_range': [0, 400],
                    'field_name': 'calibration_subwindows_root_mean_square_win1',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'calibration_subwindows_root_mean_square_win1',
                    'show': True,
                    'title': 'Wavelength calibration subwindows RMS (window 1)',
                    'units': 'nm'
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-0.05, 0.05],
                    'field_name': 'calibration_subwindows_shift_win2',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'calibration_subwindows_shift_win2',
                    'show': True,
                    'title': 'Wavelength calibration subwindows shift (window 2)',
                    'units': 'nm'
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-0.05, 0.05],
                    'field_name': 'calibration_subwindows_squeeze_win2',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'calibration_subwindows_squeeze_win2',
                    'show': True,
                    'title': 'Wavelength calibration subwindows squeeze (window 2)',
                    'units': ''
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-0.05, 0.05],
                    'field_name': 'calibration_polynomial_coefficients_win2',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'calibration_polynomial_coefficients_win2',
                    'show': True,
                    'title': 'Wavelength calibration polynomial coefficients (window 2)',
                    'units': ''
                },
                {
                    'color_scale': 'Blues',
                    'data_range': [0, 400],
                    'field_name': 'calibration_subwindows_root_mean_square_win2',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'calibration_subwindows_root_mean_square_win2',
                    'show': True,
                    'title': 'Wavelength calibration subwindows RMS (window 2)',
                    'units': ''
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-0.005, 0.005],
                    'field_name': 'calibration_subwindows_shift_win3',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'calibration_subwindows_shift_win3',
                    'show': True,
                    'title': 'Wavelength calibration subwindows shift (window 3)',
                    'units': 'nm'
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-0.005, 0.005],
                    'field_name': 'calibration_subwindows_squeeze_win3',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'calibration_subwindows_squeeze_win3',
                    'show': True,
                    'title': 'Wavelength calibration subwindows squeeze (window 3)',
                    'units': ''
                },
                {
                    'color_scale': 'RdBu',
                    'data_range': [-0.005, 0.005],
                    'field_name': 'calibration_polynomial_coefficients_win3',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'calibration_polynomial_coefficients_win3',
                    'show': True,
                    'title': 'Wavelength calibration polynomial coefficients (window 3)',
                    'units': ''
                },
                {
                    'color_scale': 'Blues',
                    'data_range': [0, 400],
                    'field_name': 'calibration_subwindows_root_mean_square_win3',
                    'flag': False,
                    'log_range': False,
                    'primary_variable': 'calibration_subwindows_root_mean_square_win3',
                    'show': True,
                    'title': 'Wavelength calibration subwindows RMS (window 3)',
                    'units': ''
                },
            ]
        }
    }

    tmpl = 'S5P_OPER_CFG_MPC_L2_00000000T000000_99999999T999999_{0:%Y%m%dT%H%M%S}.xml'
    fname = tmpl.format(datetime.datetime.utcnow())
    with open(fname, 'w', encoding='utf-8') as fref:
        print(plistlib.dumps(d).decode('UTF-8'), file=fref)
