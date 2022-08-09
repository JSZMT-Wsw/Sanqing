#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import platform
import sys
import os
import re
import logging
from datetime import datetime, timedelta
from collections import OrderedDict
import plistlib
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

from lxml import etree
import numpy, netCDF4, h5py  # only for version numbers

from pycama import __version__


def split_input_files(input_files, mode, mission="S5P", relative=False):
    rval = OrderedDict()
    for f in input_files:
        if mission == "S5P" or mission == 'G2A':
            file_mode = os.path.basename(f)[4:8]
            if file_mode != mode:
                continue
            key = os.path.basename(f)[9:19]
        elif mission == "OMI":
            key = os.path.basename(f).split('_')[1][3:]
        elif mission == 'QA4ECV':
            key = "{0:6s}".format(os.path.basename(f).split('_')[2]).replace(" ", "_")
        if key not in rval:
            rval[key] = []
        if relative:
            rval[key].append(f)
        else:
            rval[key].append(os.path.abspath(f))
    return rval


def synth_output_files(grouped_input_files, mode="OFFL", report=False, report_loc=None, mission="S5P", label=None):
    if report_loc is None:
        report_loc = os.path.curdir
    else:
        report_loc = os.path.abspath(report_loc)
    rval = OrderedDict()
    now = datetime.utcnow()
    fmt = "S5P_{mode}_{key}_{start:%Y%m%dT%H%M%S}_{end:%Y%m%dT%H%M%S}_{now:%Y%m%dT%H%M%S}"
    short_fmt = "S5P_{mode}_{key}_{start:%Y%m%d}"
    for key in grouped_input_files.keys():
        if mission == "S5P" or mission == 'G2A':
            start_times = [datetime.strptime(os.path.basename(f)[20:35], "%Y%m%dT%H%M%S") for f in
                           grouped_input_files[key]]
            end_times = [datetime.strptime(os.path.basename(f)[36:51], "%Y%m%dT%H%M%S") for f in
                         grouped_input_files[key]]
            new_key = "MPC_" + key[4:]
            start_time = min(start_times)
            end_time = max(start_times)
            rval[new_key] = fmt.format(mode=mode, key=new_key, start=start_time, end=end_time, now=now)
            if label is not None:
                rval[new_key] = rval[new_key] + "_" + label
            rval[new_key] = rval[new_key] + ".nc"
        elif mission == "OMI":
            mode = "OFFL"
            f = grouped_input_files[key][0]
            new_key = "MPC_" + os.path.basename(f).split('_')[1][3:]
            start_times = [datetime.strptime(os.path.basename(f).split('_')[2][0:9], "%Ym%m%d") for f in
                           grouped_input_files[key]]
            start_time = min(start_times)
            end_time = max(start_times)
            if start_time == end_time:
                end_time = end_time + timedelta(days=1)
            rval[new_key] = fmt.format(mode=mode, key=new_key, start=start_time, end=end_time, now=now)
            if label is not None:
                rval[new_key] = rval[new_key] + "_" + label
            rval[new_key] = rval[new_key] + ".nc"
        elif mission == 'QA4ECV':
            # QA4ECV_L2_NO2_OMI_20110505T000900_o36184_fitB_v1.nc
            mode = "OFFL"
            f = grouped_input_files[key][0]
            new_key = "MPC_{0:6s}".format(os.path.basename(f).split('_')[2]).replace(" ", "_")
            start_times = [datetime.strptime(os.path.basename(f).split('_')[4], "%Y%m%dT%H%M%S") for f in
                           grouped_input_files[key]]
            start_time = min(start_times)
            end_time = max(start_times)
            if start_time == end_time:
                end_time = end_time + timedelta(days=1)
            rval[new_key] = fmt.format(mode=mode, key=new_key, start=start_time, end=end_time, now=now)
            if label is not None:
                rval[new_key] = rval[new_key] + "_" + label
            rval[new_key] = rval[new_key] + ".nc"

        if report:
            if mission == "S5P" or mission == 'G2A':
                new_key = "REP_" + key[4:]
                rval[new_key] = os.path.join(report_loc,
                                             short_fmt.format(mode=mode, key=new_key, start=min(start_times)))
                if label is not None:
                    rval[new_key] = rval[new_key] + "_" + label
                rval[new_key] = rval[new_key] + ".tex"
            elif mission == "OMI":
                f = grouped_input_files[key][0]
                new_key = "REP_" + os.path.basename(f).split('_')[1][3:]
                rval[new_key] = os.path.join(report_loc, short_fmt.format(mode=mode, key=new_key, start=start_time))
                if label is not None:
                    rval[new_key] = rval[new_key] + "_" + label
                rval[new_key] = rval[new_key] + ".tex"
            elif mission == "QA4ECV":
                f = grouped_input_files[key][0]
                new_key = "REP_{0:6s}".format(os.path.basename(f).split('_')[2]).replace(" ", "_")
                rval[new_key] = os.path.join(report_loc, short_fmt.format(mode=mode, key=new_key, start=start_time))
                if label is not None:
                    rval[new_key] = rval[new_key] + "_" + label
                rval[new_key] = rval[new_key] + ".tex"
    return rval


def list_tree(base, mode="OFFL", mission="S5P", date=None, filetype=".nc", product=None):
    rval = []
    for root, dirs, files in os.walk(base):
        for f in files:
            if mission == "OMI" and f.endswith(filetype) and f.startswith(mission):
                if product is not None:
                    if f.split('_')[1] != "L2-" + product:
                        print("Skipping {0} because product does not match ({1}/{2})".format(f, f.split('_')[1],
                                                                                             "L2-" + product))
                        continue
                if date is None:
                    rval.append(os.path.join(root, f))
                else:
                    try:
                        if datetime.strptime(f.split('_')[2][0:9], "%Ym%m%d") == date:
                            rval.append(os.path.join(root, f))
                    except ValueError:
                        print("Could not parse time in input file, skipping {0}".format(f))
            elif (os.path.basename(f)[4:8] == mode
                  and f.endswith(filetype)
                  and f.startswith(mission)):
                if os.path.basename(f)[13:19] != product:
                    print("Skipping {0} because product does not match ({1}/{2})".format(os.path.basename(f),
                                                                                         os.path.basename(f)[13:19],
                                                                                         product))
                    continue

                if date is None:
                    rval.append(os.path.join(root, f))
                else:
                    try:
                        ref = netCDF4.Dataset(os.path.join(root, f), 'r')
                    except (IOError, OSError):
                        print("Could not open input file, skipping {0}".format(f))
                    else:
                        with ref:
                            try:
                                ref_date = ref.time_reference[0:19]
                            except AttributeError:
                                print("Could not parse time in input file, skipping {0}".format(f))
                                continue
                            try:
                                if datetime.strptime(ref_date, "%Y-%m-%dT%H:%M:%S") == date:
                                    rval.append(os.path.join(root, f))
                            except ValueError:
                                print("Could not parse time in input file, skipping {0}".format(f))

    return rval


def main(product, mode, config_files, input_files, output_file, create_report=False,
         log_level="INFO", sensing_times=None, report_only=False, append=False,
         report_loc=None, verbose=False, mission="S5P", relative=False, label=None):
    jo = etree.Element('Ipf_Job_Order')
    conf = etree.SubElement(jo, 'Ipf_Conf')
    elem = etree.SubElement(conf, 'Processor_Name')
    elem.text = product
    elem = etree.SubElement(conf, 'Version')
    elem.text = __version__
    elem = etree.SubElement(conf, 'Stdout_Log_Level')
    elem.text = log_level
    elem = etree.SubElement(conf, 'Stderr_Log_Level')
    elem.text = "ERROR"
    elem = etree.SubElement(conf, 'Test')
    elem.text = 'false'
    elem = etree.SubElement(conf, 'Breakpoint_Enable')
    elem.text = 'false'
    elem = etree.SubElement(conf, 'Processing_Station')
    try:
        print("hosename")
        # elem.text = os.uname().nodename.split('.')[-2].upper()
        elem.text = "H"
    except IndexError:
        elem.text = "Unknown"

    cfg_files = etree.SubElement(conf, 'Config_Files')  # , attrib={'count':"{0}".format(len(config_files)))
    for f in config_files:
        elem = etree.SubElement(cfg_files, 'Conf_File_Name')
        elem.text = f

    sens = etree.SubElement(conf, 'Sensing_Time')
    if sensing_times is None:
        sensing_times = "00000000_000000000000", "99999999_999999999999"
    else:
        sensing_times = [t.strftime("%Y%m%d_%H%M%S%f") for t in sensing_times]
    for n, t in zip(["Start", "Stop"], sensing_times):
        elem = etree.SubElement(sens, n)
        elem.text = t

    dproc = etree.SubElement(conf, "Dynamic_Processing_Parameters")
    # dpp = {'Processing_Mode': mode, 'Report_Only': str(report_only).lower(), 'Append_To_Output': str(append).lower()}
    dpp = {'Processing_Mode': mode, 'Report_Only': 'false', 'Append_To_Output': 'false'}
    for k, v in dpp.items():
        ppar = etree.SubElement(dproc, "Processing_Parameter")
        elem = etree.SubElement(ppar, "Name")
        elem.text = k
        elem = etree.SubElement(ppar, "Value")
        elem.text = v

    procs = etree.SubElement(jo, 'List_of_Ipf_Procs', attrib={'count': "1"})

    proc = etree.SubElement(procs, 'Ipf_Proc')
    elem = etree.SubElement(proc, 'Task_Name')
    elem.text = "PyCAMA"
    elem = etree.SubElement(proc, 'Task_Version')
    elem.text = __version__

    grouped_input_files = split_input_files(input_files, mode, mission=mission, relative=relative)
    input_file_types = list(grouped_input_files.keys())

    inputs_elem = etree.SubElement(proc, 'List_of_Inputs', attrib={'count': "{0}".format(len(input_file_types))})
    for ftype in input_file_types:
        if verbose:
            print("Found {0} files of type {1}".format(len(grouped_input_files[ftype]), ftype))
        input_elem = etree.SubElement(inputs_elem, 'Input')
        elem = etree.SubElement(input_elem, 'File_Type')
        elem.text = ftype
        elem = etree.SubElement(input_elem, 'File_Name_Type')
        elem.text = "Physical"
        file_names_elem = etree.SubElement(input_elem, "List_of_File_Names",
                                           attrib={"count": "{0}".format(len(grouped_input_files[ftype]))})
        files = sorted(grouped_input_files[ftype], key=os.path.basename)
        for fname in files:
            elem = etree.SubElement(file_names_elem, "File_Name")
            elem.text = fname

    output_files = synth_output_files(grouped_input_files, mode=mode, report=create_report, report_loc=report_loc,
                                      mission=mission, label=label)

    outputs_elem = etree.SubElement(proc, "List_of_Outputs", attrib={"count": "{0}".format(len(output_files.keys()))})
    for ftype in output_files.keys():
        output_elem = etree.SubElement(outputs_elem, 'Output')
        elem = etree.SubElement(output_elem, 'File_Type')
        elem.text = ftype
        elem = etree.SubElement(output_elem, 'File_Name_Type')
        elem.text = "Physical"
        elem = etree.SubElement(output_elem, 'File_Name')
        elem.text = output_files[ftype]

    with open(output_file, "w") as fref:
        print(etree.tostring(jo, xml_declaration=True, encoding='utf-8', pretty_print=True).decode('utf-8'), file=fref)


def dt_input(string):
    import argparse

    try:
        dt = datetime.strptime(string, "%Y-%m-%d")
    except ValueError as err:
        try:
            dt = datetime.strptime(string, "%Y-%m-%dT%H:%M:%S")
        except ValueError as err:
            raise argparse.ArgumentTypeError(str(err))
    return dt


if __name__ == "__main__":
    import argparse

    # product, mode, config_files, input_files, output_file, create_report=False, log_level="INFO", sensing_times=None, report_only=False, append=False
    parser = argparse.ArgumentParser(description='Create PyCAMA joborder files')
    parser.add_argument('-v', '--verbose', action='store_true', help="Be chatty")
    parser.add_argument('-p', '--product', help='The product key for processing', default="FRESCO")
    parser.add_argument('-m', '--mode', choices=("OFFL", "NRTI", "RPRO", "TEST", "OPER"),
                        help="The processing mode (ignored for OMI)", default="OFFL")
    parser.add_argument('-c', '--cfg', metavar="FILE", required=True, help='The configuration file(s)', nargs="+")
    parser.add_argument('-M', '--mission', default="S5P", help="Mission to search for")
    parser.add_argument('-d', '--dir', metavar="DIR", help="Basedir when searching for input files")
    parser.add_argument('-D', '--date', metavar="YYYY-MM-DD", type=dt_input,
                        help='Limit file searching to this date (without setting the sensing times)')
    parser.add_argument('-i', '--input', metavar="FILE", nargs="+", help="explicit list of files")
    parser.add_argument('-o', '--output', metavar="FILE", help="The job order filename")
    parser.add_argument('-r', '--report', action="store_true", help="Create a report")
    parser.add_argument('-l', '--log', choices=("DEBUG", "INFO", "WARNING"), default="INFO",
                        help="Set the logging level")
    parser.add_argument('-s', '--sensing', metavar='DATE', nargs=2, type=dt_input,
                        help="Sensing time as YYYY-mm-dd[THH:MM:SS]", default=None)
    parser.add_argument('-R', '--report-only', action="store_true", help="Only create a report")
    parser.add_argument('-L', '--report-location', help='The directory where the report should be placed.')
    parser.add_argument('-a', '--append', action="store_true", help="Append to existing file")
    parser.add_argument('-f', '--filetype', help="File extension of input files", default=".nc")
    parser.add_argument('--relative', help="Use relative paths", action='store_true')
    parser.add_argument('--label', help="Extra label for output file name")

    args = parser.parse_args()

    if args.dir is not None:
        input_files = list_tree(args.dir, mode=args.mode,
                                mission=args.mission, date=args.date,
                                filetype=args.filetype, product=args.product)
    elif args.input is not None:
        input_files = args.input
    else:
        parser.print_help(file=sys.stderr)
        print("No input files specified", file=sys.stderr)
        sys.exit(1)

    main(args.product, args.mode, args.cfg, input_files, args.output,
         create_report=args.report, log_level=args.log,
         sensing_times=args.sensing, report_only=args.report_only,
         append=args.append, report_loc=args.report_location,
         verbose=args.verbose, mission=args.mission, relative=args.relative, label=args.label)

    # d = E:\Professional\Anaconda3\python.exe D:/00000Aerosol/Tropomi/tropomi_L3/PyCAMA_config_generator.py -p NO2___ -m NRTI -c D:\00000Aerosol\Tropomi\tropomi_L3\S5P_OPER_CFG_MPC_L2_00000000T000000_99999999T999999_20200529T065905.xml -d D:/00000Aerosol/Tropomi/tropomi_data -D 2020-05-28 -o D:\00000Aerosol\Tropomi\no_jobFolder\no2_jobfile
