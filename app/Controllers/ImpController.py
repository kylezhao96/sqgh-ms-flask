import datetime
import json
import os
import zipfile
from pathlib import Path

import pandas as pd
import numpy as np
import xlrd
from flask import request, send_from_directory, make_response, Blueprint
from xlutils.copy import copy
from dateutil.relativedelta import *

import shutil
from app.Vendor.Utils import Utils
from app.Controllers.BaseController import BaseController
from app import api


# 测试
@api.route('/imp/test', methods=['GET'])
def test():
    print('开始执行-----')
    trans_rbb_file(r'/Users/kyle/Desktop/2021年石桥风电场日报表(5月27日换表后).xlsx',
                   datetime.datetime.strptime('2021-8', '%Y-%m'),
                   '/Users/kyle/Desktop/test',
                   os.path.join('template', 'imp', 'template'))


# 上传（集成解压和压缩功能）
@api.route('/imp/upload', methods=['POST'])
def get_wt_data():
    file_month = request.form['fileMonth']
    file_date = datetime.datetime.strptime(file_month, '%Y-%m')
    print(file_date)
    wt_file = request.files['wtFile']  # 风机单机数据
    cft_file = request.files['cftFile']  # 测风塔数据
    gz_file = request.files['gzFile']  # 风机故障数据
    rbb_file = request.files['rbbFile']  # 日报表数据
    # 定义路径
    time_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    source_path = os.path.join('template', 'imp', 'source_files', time_str)
    os.mkdir(source_path)
    exp_path = os.path.join('template', 'imp', 'exp_files', time_str)
    os.mkdir(exp_path)
    temp_path = os.path.join('template', 'imp', 'template')
    # 清除缓存
    clean_cache(os.path.dirname(source_path), 3660)
    clean_cache(os.path.dirname(exp_path), 3660)
    # 执行数据转换
    trans_wt_file(wt_file, file_date, source_path, exp_path, temp_path)
    trans_gz_files(gz_file, file_date, exp_path, temp_path)
    trans_cft_files(cft_file, file_date, exp_path, temp_path)
    trans_rbb_file(rbb_file, file_date, exp_path, temp_path)
    # 打包
    exp_file_name = '智慧风电数据' + file_month + '.zip'
    compress_files(exp_path, exp_file_name)
    response = make_response(
        send_from_directory(os.path.abspath(exp_path), exp_file_name, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(exp_file_name.encode().decode('latin-1'))
    return response


def trans_wt_file(file, file_date, source_path, exp_path, temp_path):
    """
    风机单机数据处理
    :param temp_path:
    :param exp_path:
    :param source_path:
    :param file:
    :param file_date:
    :return:
    """
    # 前期步骤 - 解压
    source_path = os.path.join(source_path, '单机数据')
    exp_path = os.path.join(exp_path, '单机数据')
    temp_path = os.path.join(temp_path, '石桥子风电场_单机数据')
    print('执行风机单机数据转换，解压地址：' + source_path + '导出地址' + exp_path)
    unpack_files(file, source_path)
    if not os.path.exists(exp_path):
        os.mkdir(exp_path)
    for line in os.listdir(source_path):
        for csv in os.listdir(source_path + '/' + line):
            csv_data = pd.read_csv(source_path + '/' + line + '/' + csv, encoding='gbk').fillna(0)
            csv_colums = csv_data.columns.values
            wt_id = csv_data.values[0][0]
            print('开始写入风机' + wt_id)
            wb_list = []
            for template_file in os.listdir(temp_path):
                if template_file[0:3] == wt_id:
                    wb_list.append(xlrd.open_workbook(temp_path + '/' + template_file, formatting_info=True))
            row_num = 1
            wb = copy(wb_list[0])
            ws = wb.get_sheet(0)
            for i, row in enumerate(csv_data.values):
                # print('读取' + source_path + '/' + line + '/' + csv + str(i) + '行')
                time = row[int(np.argwhere(csv_colums == '时间'))]
                if len(time) < 17:
                    dt = datetime.datetime.strptime(time, '%Y/%m/%d %H:%M')
                else:
                    dt = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                if file_date.month != dt.month:
                    continue
                # print('写入' + exp_path + '/' + os.listdir(temp_path)[
                #     int(wt_id[1: 3]) - 1] + ' ' + str(row_num) + '行')
                ws.write(row_num, 0, dt.strftime('%Y/%m/%d %H:%M:%S'))
                if '风速平均' in csv_colums:
                    ws.write(row_num, 1, row[int(np.argwhere(csv_colums == '风速平均'))])
                if '风速' in csv_colums:
                    ws.write(row_num, 1, row[int(np.argwhere(csv_colums == '风速'))])
                if '有功功率平均' in csv_colums:
                    ws.write(row_num, 2, row[int(np.argwhere(csv_colums == '有功功率平均'))])
                if '发电机有功功率' in csv_colums:
                    ws.write(row_num, 2, row[int(np.argwhere(csv_colums == '发电机有功功率'))])
                row_num = row_num + 1
            wb.save(exp_path + '/' + os.listdir(temp_path)[int(wt_id[1: 3]) - 1])
    # shutil.rmtree(source_path)  # 删除源文件夹
    # os.remove(source_path)
    print('执行风机单机数据转换成功！')
    # compress_files(exp_path, '风机单机数据.zip')


def unpack_files(file, unpack_path):
    """
    解压程序
    :param file:
    :param unpack_path:
    :return:
    """
    # 判断解压路径是否存在
    print('开始压缩，压缩文件名：' + file.filename + '解压地址：' + unpack_path)
    if not os.path.exists(unpack_path):
        os.mkdir(unpack_path)
    try:
        with zipfile.ZipFile(file, 'r') as f:
            # for fn in f.namelist():
            #     extracted_path = Path(f.extract(fn, path=unpack_path))
            #     extracted_path.rename(os.path.join(Path(unpack_path), fn.encode('cp437').decode('gbk')))
            f.extractall(path=unpack_path)
    except Exception as e:
        print("异常对象的类型是:%s" % type(e))
        print("异常对象的内容是:%s" % e)
    finally:
        print('解压结束')


def compress_files(compress_dir, save_file_name, save_path=None):
    """
    压缩程序
    :param compress_dir: 压缩的文件夹路径
    :param save_path: 压缩文件保存路径
    :param save_file_name: 压缩文件名
    :return:
    """
    if save_path is None:
        save_path = compress_dir
    else:
        # 判断保存是否存在
        if not os.path.exists(save_path):
            os.mkdir(save_path)
    print('开始压缩文件，被压缩目录:' + compress_dir + '保存路径为:' + save_path + '保存文件名:' + save_file_name)
    pre_path = os.path.abspath(os.getcwd())
    try:
        os.chdir(save_path)
        with zipfile.ZipFile(save_file_name, 'w') as zf:
            os.chdir(pre_path)
            os.chdir(compress_dir)
            for root, dirs, files in os.walk(os.getcwd()):
                # print(root)
                for file in files:
                    # print(file)
                    if file.endswith('.xls'):
                        zf.write(os.path.join(os.path.relpath(root), file), compress_type=zipfile.ZIP_DEFLATED)
    except Exception as e:
        print("异常对象的类型是:%s" % type(e))
        print("异常对象的内容是:%s" % e)
    finally:
        zf.close()
        os.chdir(pre_path)
        print('压缩程序结束')


def clean_cache(cache_path, stay_time=86400, max_num=5):
    """
    清除路径缓存文件
    :param max_num:
    :param cache_path: 缓存路径
    :param stay_time: 缓存保留时间，默认86400秒
    :return:
    """
    # 如果已存在解压数据，先删除上次数据（现设定多于1天清除86400），以免占用空间
    print('开始清除缓存文件，需清除缓存路径为' + cache_path + '最大保存时间为' + str(stay_time) + 's,最大文件夹数量为' + str(max_num))
    if len(os.listdir(cache_path)) > max_num:
        rm_num = len(os.listdir(cache_path)) - max_num
        for child_path in os.listdir(cache_path):
            if rm_num <= 0:
                break
            if (datetime.datetime.now() - datetime.datetime.strptime(child_path,
                                                                     '%Y%m%d%H%M%S')).seconds > stay_time:
                shutil.rmtree(os.path.join(cache_path, child_path))
            rm_num = rm_num - 1
    print('清除缓存文件结束')


# 判断是否存在压缩文件
@api.route('/imp/download/is-exist', methods=['get'])
def isExistedFile():
    dir_list = os.listdir(os.path.join('template', 'imp', 'exp_files'))
    if len(dir_list) > 0:
        return BaseController().successData(
            result='存在' if os.path.exists(
                os.path.join('template', 'imp', 'exp_files', dir_list[-1], '智慧风电数据.zip')) else '不存在'
        )
    else:
        return BaseController().successData(result='不存在')


# 下载压缩文件
@api.route('/imp/download/latest', methods=['POST'])
def download_latest_file():
    file_name = '智慧风电数据.zip'
    dir_list = os.listdir(os.path.join('template', 'imp', 'exp_files'))
    if len(dir_list) > 0:
        response = make_response(
            send_from_directory(os.path.join(os.getcwd(), 'template', 'imp', 'exp_files', dir_list[-1]), file_name,
                                as_attachment=True))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(file_name.encode().decode('latin-1'))
        return response
    else:
        return BaseController().error(msg='文件不存在！')


def trans_gz_files(file, file_date, exp_path, temp_path):
    """
    风机故障文件转化
    :param file_date:
    :param temp_path:
    :param exp_path:
    :param file: 故障文件
    :return:
    """
    gz_df = pd.read_csv(file, encoding='gbk')
    exp_path = os.path.join(exp_path, '停机数据')
    exp_file = os.path.join(exp_path, '石桥子风电场_停机数据.xls')
    temp_file = os.path.join(temp_path, '石桥子风电场_停机数据.xls')
    # year = datetime.datetime.strptime(gz_df.loc[0][1], '%Y-%m-%d %H:%M:%S').year
    if os.path.exists(exp_file):
        wb = xlrd.open_workbook(exp_file, formatting_info=True)
    else:
        if not os.path.exists(exp_path):
            os.makedirs(exp_path)
        wb = xlrd.open_workbook(temp_file, formatting_info=True)
    wb_copy = copy(wb)
    ws_copy = wb_copy.get_sheet(0)
    row_num = 2
    for row in gz_df.values:
        if file_date <= datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') < file_date + relativedelta(months=+1):
            ws_copy.write(row_num, 0, trans_double_id(row[5]))
            ws_copy.write(row_num, 1, datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d '
                                                                                                       '%H:%M:%S'))
            ws_copy.write(row_num, 2, datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d '
                                                                                                       '%H:%M:%S'))
            ws_copy.write(row_num, 3, row[7])
            row_num = row_num + 1
    wb_copy.save(os.path.join(exp_path, '石桥子风电场_停机数据.xls'))


def trans_cft_files(file, file_date, exp_path, temp_path):
    """
    测风塔数据转化
    :param file:
    :param file_date:
    :param exp_path:
    :param temp_path:
    :return:
    """
    exp_path = os.path.join(exp_path, '上网电量&功率&测风塔数据')
    exp_file = os.path.join(exp_path, '石桥子风电场_上网电量&功率&测风塔数据.xls')
    temp_file = os.path.join(temp_path, '石桥子风电场_上网电量&功率&测风塔数据.xls')
    cft_xls = pd.ExcelFile(file)  # 读取测风塔数据，单表可能有多个sheet
    if os.path.exists(exp_file):
        wb = xlrd.open_workbook(exp_file, formatting_info=True)
    else:
        if not os.path.exists(exp_path):
            os.mkdir(exp_path)
        wb = xlrd.open_workbook(temp_file, formatting_info=True)
    wb_cft = copy(wb)
    ws_cft = wb_cft.get_sheet(2)
    row_num = 1
    for name in cft_xls.sheet_names:
        df = pd.read_excel(cft_xls, sheet_name=name)
        header = df.columns
        for row in df.values:
            if not (file_date <= row[int(np.argwhere(header == 'TIME'))] < file_date + relativedelta(
                    months=+1)):
                continue
            ws_cft.write(row_num, 0, row[int(np.argwhere(header == 'TIME'))].strftime('%Y-%m-%d %H:%M:%S'))  # 时间
            # if row[int(np.argwhere(header == 'PRESSURE'))] == 0:
            #     continue
            ws_cft.write(row_num, 1, row[int(np.argwhere(header == 'V7AVGSP'))])  # 风速
            ws_cft.write(row_num, 2, row[int(np.argwhere(header == 'V7AVGDIR'))])  # 风向
            ws_cft.write(row_num, 3, row[int(np.argwhere(header == 'V1TEMP'))])  # 温度
            ws_cft.write(row_num, 4, row[int(np.argwhere(header == 'PRESSURE'))])  # 压强
            ws_cft.write(row_num, 5, row[int(np.argwhere(header == 'V1HUM'))])  # 湿度
            row_num = row_num + 1
    wb_cft.save(exp_file)


def trans_double_id(wt_id):
    """
    :param wt_id: string 风机号
    :return: wt_double_id 双重编号
    """
    if not wt_id.startswith('A'):
        wt_id = wt_id[1:]
    if int(wt_id[1:]) <= 10:
        return 'A' + (wt_id[1:]).zfill(2) + '-312' + str(11 - int(wt_id[1:])).zfill(2)
    elif int(wt_id[1:]) <= 20:
        return 'A' + (wt_id[1:]).zfill(2) + '-313' + str(21 - int(wt_id[1:])).zfill(2)
    elif int(wt_id[1:]) <= 30:
        return 'A' + (wt_id[1:]).zfill(2) + '-322' + str(31 - int(wt_id[1:])).zfill(2)
    else:
        return 'A' + (wt_id[1:]).zfill(2) + '-323' + str(41 - int(wt_id[1:])).zfill(2)


def trans_rbb_file(file, file_date, exp_path, temp_path):
    """
    转换日报表文件
    :param file:
    :param file_date:
    :param exp_path:
    :param temp_path:
    :return:
    """
    # 写入上网电量
    cdf_dl = pd.read_excel(file, sheet_name='日报计算表', usecols=range(76), skiprows=range(4), header=None)
    temp_dl_file = os.path.join(temp_path, '石桥子风电场_上网电量&功率&测风塔数据.xls')
    exp_dl_path = os.path.join(exp_path, '上网电量&功率&测风塔数据')
    exp_dl_file = os.path.join(exp_dl_path, '石桥子风电场_上网电量&功率&测风塔数据.xls')
    if os.path.exists(exp_dl_file):
        wb = xlrd.open_workbook(exp_dl_file, formatting_info=True)
    else:
        if not os.path.exists(exp_dl_path):
            os.mkdir(exp_dl_path)
        wb = xlrd.open_workbook(temp_dl_file, formatting_info=True)
    wb_copy_sw = copy(wb)
    ws_copy = wb_copy_sw.get_sheet(0)
    row_num = 1
    for row in cdf_dl.values:
        if file_date <= row[0] < file_date + relativedelta(months=+1):
            ws_copy.write(row_num, 0, row[0].strftime('%Y/%m/%d'))
            ws_copy.write(row_num, 1, Utils.realRound(row[32] / 1000, 3))
            row_num = row_num + 1
        elif row[0] >= file_date + relativedelta(months=+1):
            break
    wb_copy_sw.save(exp_dl_file)
    # 停机数据
    temp_tj_file = os.path.join(temp_path, '石桥子风电场_停机数据.xls')
    exp_tj_path = os.path.join(exp_path, '停机数据')
    exp_tj_file = os.path.join(exp_tj_path, '石桥子风电场_停机数据.xls')
    if os.path.exists(exp_tj_file):
        wb = xlrd.open_workbook(exp_tj_file, formatting_info=True)
    else:
        if not os.path.exists(exp_tj_path):
            os.mkdir(exp_tj_path)
        wb = xlrd.open_workbook(temp_tj_file, formatting_info=True)
    wb_copy_wh = copy(wb)
    ws_copy_wh = wb_copy_wh.get_sheet(2)
    row_num = 2
    # 写入维护数据
    cdf_wh = pd.read_excel(file, sheet_name='风机维护统计', header=None)
    for row in cdf_wh.values:
        if str(row[0]).strip().startswith('A'):
            try:
                # row_date = datetime.datetime.strptime(row[3], '%Y/%m/%d %H:%M')
                if file_date <= row[3] < file_date + relativedelta(months=+1):
                    ws_copy_wh.write(row_num, 0, trans_double_id(row[0].strip()[0:3]))
                    ws_copy_wh.write(row_num, 1, row[3].strftime('%Y-%m-%d %H:%M:%S'))
                    ws_copy_wh.write(row_num, 2, row[4].strftime('%Y-%m-%d %H:%M:%S'))
                    ws_copy_wh.write(row_num, 3, row[2])
                    row_num = row_num + 1
                elif row[3] >= file_date + relativedelta(months=+1):
                    break
            except Exception as e:
                print(e)
                print(row[0])
                print(row[3])
                print(row[8])
                print(row[11])
                continue
        elif str(row[0]).strip().startswith('3'):
            try:
                # row_date = datetime.datetime.strptime(row[3], '%Y/%m/%d %H:%M')
                if file_date <= row[3] < file_date + relativedelta(months=+1):
                    ws_copy_wh.write(row_num, 0, trans_double_id(row[0].strip()[6:-1]))
                    ws_copy_wh.write(row_num, 1, row[3].strftime('%Y-%m-%d %H:%M:%S'))
                    ws_copy_wh.write(row_num, 2, row[4].strftime('%Y-%m-%d %H:%M:%S'))
                    ws_copy_wh.write(row_num, 3, row[2])
                    row_num = row_num + 1
                elif row[3] >= file_date + relativedelta(months=+1):
                    break
            except Exception as e:
                print(e)
                print(row[0])
                print(row[3])
                print(row[8])
                print(row[11])
                continue
        if str(row[8]).strip().startswith('A'):
            try:
                # row_date = datetime.datetime.strptime(row[11], '%Y/%m/%d %H:%M')
                if file_date <= row[11] < file_date + relativedelta(months=+1):
                    ws_copy_wh.write(row_num, 0, trans_double_id(row[8].strip()[0:3]))
                    ws_copy_wh.write(row_num, 1, row[11].strftime('%Y-%m-%d %H:%M:%S'))
                    ws_copy_wh.write(row_num, 2, row[12].strftime('%Y-%m-%d %H:%M:%S'))
                    ws_copy_wh.write(row_num, 3, row[10])
                    row_num = row_num + 1
                elif row[11] >= file_date + relativedelta(months=+1):
                    break
            except Exception as e:
                print(e)
                print(row[0])
                print(row[3])
                print(row[8])
                print(row[11])
                continue
        elif str(row[8]).strip().startswith('3'):
            try:
                # row_date = datetime.datetime.strptime(row[11], '%Y/%m/%d %H:%M')
                if file_date <= row[11] < file_date + relativedelta(months=+1):
                    ws_copy_wh.write(row_num, 0, trans_double_id(row[8].strip()[6:-1]))
                    ws_copy_wh.write(row_num, 1, row[11].strftime('%Y-%m-%d %H:%M:%S'))
                    ws_copy_wh.write(row_num, 2, row[12].strftime('%Y-%m-%d %H:%M:%S'))
                    ws_copy_wh.write(row_num, 3, row[10])
                    row_num = row_num + 1
                elif row[11] >= file_date + relativedelta(months=+1):
                    break
            except Exception as e:
                print(e)
                print(row[0])
                print(row[3])
                print(row[8])
                print(row[11])
                continue
    # 写入输变电维护记录
    cdf_sbd_wh = pd.read_excel(file, sheet_name='输变电故障、维护统计', header=None)
    for row in cdf_sbd_wh.values:
        # 先统计一期
        if str(row[0]).strip() in ['全场停电', '全厂停电', '#1集电线路、#2集电线路', '#1集电线路', '#2集电线路']:
            try:
                # 全场停电情况
                if str(row[0]).strip() in ['全场停电', '全厂停电', '#1集电线路、#2集电线路']:
                    wt_range = range(1, 21)
                # #1线
                elif str(row[0]).strip() == '#1集电线路':
                    wt_range = range(1, 11)
                # #2线
                elif str(row[0]).strip() == '#2集电线路':
                    wt_range = range(11, 21)
                if file_date <= row[3] < file_date + relativedelta(months=+1):
                    for wid in wt_range:
                        ws_copy_wh.write(row_num, 0, trans_double_id('A' + str(wid)))
                        ws_copy_wh.write(row_num, 1, row[3].strftime('%Y-%m-%d %H:%M:%S'))
                        ws_copy_wh.write(row_num, 2, row[4].strftime('%Y-%m-%d %H:%M:%S'))
                        ws_copy_wh.write(row_num, 3, row[0] + row[1])
                        row_num = row_num + 1
                elif row[3] >= file_date + relativedelta(months=+1):
                    break
            except Exception as e:
                print(e)
                print(row[0])
                print(row[3])
                print(row[4])
                continue
        # 统计二期
        if str(row[8]).strip() in ['全场停电', '全厂停电', '#3集电线路、#4集电线路', '#3集电线路', '#4集电线路']:
            # 全场停电情况
            try:
                # 全场停电情况
                if str(row[8]).strip() in ['全场停电', '全厂停电', '#3集电线路、#4集电线路']:
                    wt_range = range(21, 41)
                # #1线
                elif str(row[8]).strip() == '#3集电线路':
                    wt_range = range(21, 31)
                # #2线
                elif str(row[8]).strip() == '#4集电线路':
                    wt_range = range(31, 41)
                if file_date <= row[11] < file_date + relativedelta(months=+1):
                    for wid in wt_range:
                        ws_copy_wh.write(row_num, 0, trans_double_id('A' + str(wid)))
                        ws_copy_wh.write(row_num, 1, row[11].strftime('%Y-%m-%d %H:%M:%S'))
                        ws_copy_wh.write(row_num, 2, row[12].strftime('%Y-%m-%d %H:%M:%S'))
                        ws_copy_wh.write(row_num, 3, row[8] + row[9])
                        row_num = row_num + 1
                elif row[11] >= file_date + relativedelta(months=+1):
                    break
            except Exception as e:
                print(e)
                print(row[8])
                print(row[11])
                print(row[12])
                continue
    wb_copy_wh.save(exp_tj_file)
    # 写入限电数据
    wb = xlrd.open_workbook(exp_tj_file, formatting_info=True)
    wb_copy_xd = copy(wb)
    ws_copy_xd = wb_copy_xd.get_sheet(3)
    row_num = 2
    cdf_xd = pd.read_excel(file, sheet_name='电网故障、检修、限电统计', header=None)
    for row in cdf_xd.values:
        if str(row[2]).startswith('A'):
            try:
                # row_date = datetime.datetime.strptime(row[4], '%Y/%m/%d %H:%M')
                if file_date <= row[4] < file_date + relativedelta(months=+1):
                    for id in range(40):
                        if id == 6:
                            continue
                        elif id == 11:
                            continue
                        elif id == 28:
                            continue
                        elif id == 38:
                            continue
                        wt_id = 'A' + str(id + 1).zfill(2)
                        ws_copy_xd.write(row_num, 0, trans_double_id(wt_id))
                        ws_copy_xd.write(row_num, 1, row[4].strftime('%Y-%m-%d %H:%M:%S'))
                        ws_copy_xd.write(row_num, 2, row[5].strftime('%Y-%m-%d %H:%M:%S'))
                        ws_copy_xd.write(row_num, 3, '电网限电')
                        row_num = row_num + 1
                elif row[4] >= file_date + relativedelta(months=+1):
                    break
            except Exception as e:
                print("异常对象的类型是:%s" % type(e))
                print("异常对象的内容是:%s" % e)
                continue
    wb_copy_xd.save(exp_tj_file)
