import datetime
import os

from dateutil.relativedelta import relativedelta
from flask import request
from functools import reduce

from app import app, api
from app.Controllers.BaseController import BaseController
from app.Models import CalDailyForm
import pandas as pd
from openpyxl.utils import get_column_letter, column_index_from_string

from app.Models.GpPlan import GpPlan
from app.Vendor.Decorator import classTransaction
from app.Vendor.Utils import Utils, dict_merge
from app.env import config


@api.route('/basic-data/upload', methods=['POST'])
def basic_data_upload():
    """
    采用上传方式进行数据同步
    @return:
    """
    tmp = request.form['endMonth']
    start_month = datetime.datetime.strptime(request.form['startMonth'], '%Y-%m-%d') if request.form[
                                                                                            'startMonth'] != '' else ''
    end_month = datetime.datetime.strptime(request.form['endMonth'], '%Y-%m-%d') if request.form[
                                                                                        'endMonth'] != '' else ''
    rbb_file = request.files['rbbFile']  # 日报表数据
    dlfs_file = request.files['dlfsFile']  # 风机电量风速统计表
    import_cdf(rbb_file, dlfs_file, start_month.year)


@app.route('/api/cdfs', methods=['PUT'])
def syn_cdf():
    year = datetime.date.year
    cfg_rbb = {}
    cfg_dlfs = {}
    if str(year) in config.keys():
        cfg_rbb = config[str(year)]['rbb']
        cfg_dlfs = config[str(year)]['dlfs']
    else:
        cfg_rbb = config['default']['rbb']
        cfg_dlfs = config['default']['dlfs']
    pass
    # rbb_dir = config['']
    # dlfs_dir = Config.DLFS['dir']
    # import_cdf(rbb_dir, dlfs_dir)


@app.route('/api/syn/cdf', methods=['GET'])
def import_cdf(rbb_file='', year=2021, types='overwrite'):
    """
    自动化对日报表进行读取同步
    rbb_file: 日报表文件
    year: 数据年份
    type: insert 插入模式 / overwrite 覆盖模式
    """
    if str(year) in config.keys():
        cfg_rbb = config[str(year)]['rbb']
    else:
        cfg_rbb = config['default']['rbb']
    print(cfg_rbb)
    rbjsb_sheet = cfg_rbb['sheet0']
    cdf = pd.read_excel(rbb_file if rbb_file else os.path.join(cfg_rbb['dir'], cfg_rbb['name']),
                        sheet_name=rbjsb_sheet['name'],
                        usecols=range(column_index_from_string(rbjsb_sheet['end_col'])),
                        skiprows=range(rbjsb_sheet['start_row'] - 1),
                        header=None
                        )
    response = []
    for x in range(rbjsb_sheet['end_row'] - rbjsb_sheet['start_row']):
        if types == 'insert' and CalDailyForm.query.filter_by(
                date=cdf.loc[x].values[0]).first():
            continue  # 如果数据库存在本日数据，那么跳过
        if pd.isnull(cdf.loc[x].values[1]):
            # if cdf.loc[x].values[0] >= datetime.now():
            break  # 如果读到的数据不是浮点数类型，那么停止，用于判断是否到达表内空行
        # cdf_db = CalDailyForm.query.filter_by(date=cdf.loc[x + 1].values[0] + datetime.timedelta(-1)).first()
        data = {'date': cdf.loc[x].values[column_index_from_string(rbjsb_sheet['date_col']) - 1],
                'fka312': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['fka_312_col']) - 1]),
                'bka312': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['bka_312_col']) - 1]),
                'fka313': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['fka_313_col']) - 1]),
                'bka313': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['bka_313_col']) - 1]),
                'fka322': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['fka_322_col']) - 1]),
                'bka322': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['bka_322_col']) - 1]),
                'fka323': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['fka_323_col']) - 1]),
                'bka323': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['bka_323_col']) - 1]),
                'fka31b': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['fka_31b_col']) - 1]),
                'fka21b': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['fka_21b_col']) - 1]),
                'fka311': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['fka_311_col']) - 1]),
                'bka311': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['bka_311_col']) - 1]),
                'fkr311': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['fkr_311_col']) - 1]),
                'bkr311': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['bkr_311_col']) - 1]),
                'fka321': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['fka_321_col']) - 1]),
                'bka321': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['bka_321_col']) - 1]),
                'fkr321': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['fkr_321_col']) - 1]),
                'bkr321': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['bkr_321_col']) - 1]),
                'bka111': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['bka_111_col']) - 1]),
                'fka111': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['fka_111_col']) - 1]),
                'dgp1': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['dgp1_col']) - 1]),
                'donp1': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['donp1_col']) - 1]),
                'doffp1': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['doffp1_col']) - 1]),
                'dcp1': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['dcp1_col']) - 1]),
                'dcl1': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['dcl1_col']) - 1]),
                'dgp2': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['dgp2_col']) - 1]),
                'donp2': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['donp2_col']) - 1]),
                'doffp2': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['doffp2_col']) - 1]),
                'dcp2': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['dcp2_col']) - 1]),
                'dcl2': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['dcl2_col']) - 1]),
                'dgp': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['dgp_col']) - 1]),
                'donp': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['donp_col']) - 1]),
                'doffp': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['doffp_col']) - 1]),
                'dcp': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['dcp_col']) - 1]),
                'dcl': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['dcl_col']) - 1]),
                'doffp31b': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['doffp_31b_col']) - 1]),
                'doffp21b': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['doffp_21b_col']) - 1]),
                'agp1': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['agp1_col']) - 1]),
                'aonp1': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['aonp1_col']) - 1]),
                'aoffp1': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['aoffp1_col']) - 1]),
                'acp1': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['acp1_col']) - 1]),
                'acl1': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['acl1_col']) - 1]),
                'agp2': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['agp2_col']) - 1]),
                'aonp2': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['aonp2_col']) - 1]),
                'aoffp2': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['aoffp2_col']) - 1]),
                'acp2': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['acp2_col']) - 1]),
                'acl2': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['acl2_col']) - 1]),
                'agp': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['agp_col']) - 1]),
                'aonp': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['aonp_col']) - 1]),
                'aoffp': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['aoffp_col']) - 1]),
                'acp': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['acp_col']) - 1]),
                'acl': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['acl_col']) - 1]),
                'mgp1': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['mgp1_col']) - 1]),
                'monp1': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['monp1_col']) - 1]),
                'moffp1': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['moffp1_col']) - 1]),
                'mcp1': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['mcp1_col']) - 1]),
                'mcl1': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['mcl1_col']) - 1]),
                'mgp2': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['mgp2_col']) - 1]),
                'monp2': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['monp2_col']) - 1]),
                'moffp2': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['moffp2_col']) - 1]),
                'mcp2': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['mcp2_col']) - 1]),
                'mcl2': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['mcl2_col']) - 1]),
                'mgp': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['mgp_col']) - 1]),
                'monp': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['monp_col']) - 1]),
                'moffp': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['moffp_col']) - 1]),
                'mcp': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['mcp_col']) - 1]),
                'mcl': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['mcl_col']) - 1]),
                'offja311': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['doffja_311_col']) - 1]),
                'offjr311': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['doffjr_311_col']) - 1]),
                'offja321': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['doffja_321_col']) - 1]),
                'offjr321': float(cdf.loc[x].values[column_index_from_string(rbjsb_sheet['doffjr_321_col']) - 1]),
                }
        continue_flag = 0  # 设置flag用于判断是否结束本循环
        for merge_row in rbjsb_sheet['merge_row']:
            if merge_row[0] - rbjsb_sheet['start_row'] <= x < merge_row[-1] - rbjsb_sheet['start_row']:
                continue_flag = 1
                break
            if x == merge_row[-1] - rbjsb_sheet['start_row']:
                data['dgp1'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['dgp1_col']) - 1], merge_row))
                data['donp1'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['donp1_col']) - 1], merge_row))
                data['doffp1'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['doffp1_col']) - 1], merge_row))
                data['dcp1'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['dcp1_col']) - 1], merge_row))
                data['dcl1'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['dcl1_col']) - 1],
                                       merge_row))
                data['dgp2'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['dgp2_col']) - 1],
                                       merge_row))
                data['donp2'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['donp2_col']) - 1], merge_row))
                data['doffp2'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['doffp2_col']) - 1], merge_row))
                data['dcp2'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['dcp2_col']) - 1],
                                       merge_row))
                data['dcl2'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['dcl2_col']) - 1],
                                       merge_row))
                data['dgp'] = sum(map(lambda i:
                                      cdf.loc[i - rbjsb_sheet['start_row']].values[
                                          column_index_from_string(rbjsb_sheet['dgp_col']) - 1],
                                      merge_row))
                data['donp'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['donp_col']) - 1],
                                       merge_row))
                data['doffp'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['doffp_col']) - 1], merge_row))
                data['dcp'] = sum(map(lambda i:
                                      cdf.loc[i - rbjsb_sheet['start_row']].values[
                                          column_index_from_string(rbjsb_sheet['dcp_col']) - 1],
                                      merge_row))
                data['dcl'] = sum(map(lambda i:
                                      cdf.loc[i - rbjsb_sheet['start_row']].values[
                                          column_index_from_string(rbjsb_sheet['dcl_col']) - 1],
                                      merge_row))
                data['doffp31b'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['doffp_31b_col']) - 1], merge_row))
                data['doffp21b'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['doffp_21b_col']) - 1], merge_row))
                data['agp1'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['agp1_col']) - 1],
                                       merge_row))
                data['aonp1'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['aonp1_col']) - 1], merge_row))
                data['aoffp1'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['aoffp1_col']) - 1], merge_row))
                data['acp1'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['acp1_col']) - 1],
                                       merge_row))
                data['acl1'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['acl1_col']) - 1],
                                       merge_row))
                data['agp2'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['agp2_col']) - 1],
                                       merge_row))
                data['aonp2'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['aonp2_col']) - 1], merge_row))
                data['aoffp2'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['aoffp2_col']) - 1], merge_row))
                data['acp2'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['acp2_col']) - 1],
                                       merge_row))
                data['acl2'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['acl2_col']) - 1],
                                       merge_row))
                data['agp'] = sum(map(lambda i:
                                      cdf.loc[i - rbjsb_sheet['start_row']].values[
                                          column_index_from_string(rbjsb_sheet['agp_col']) - 1],
                                      merge_row))
                data['aonp'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['aonp_col']) - 1],
                                       merge_row))
                data['aoffp'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['aoffp_col']) - 1], merge_row))
                data['acp'] = sum(map(lambda i:
                                      cdf.loc[i - rbjsb_sheet['start_row']].values[
                                          column_index_from_string(rbjsb_sheet['acp_col']) - 1],
                                      merge_row))
                data['acl'] = sum(map(lambda i:
                                      cdf.loc[i - rbjsb_sheet['start_row']].values[
                                          column_index_from_string(rbjsb_sheet['acl_col']) - 1],
                                      merge_row))
                data['mgp1'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['mgp1_col']) - 1],
                                       merge_row))
                data['monp1'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['monp1_col']) - 1], merge_row))
                data['moffp1'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['moffp1_col']) - 1], merge_row))
                data['mcp1'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['mcp1_col']) - 1],
                                       merge_row))
                data['mcl1'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['mcl1_col']) - 1],
                                       merge_row))
                data['mgp2'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['mgp2_col']) - 1],
                                       merge_row))
                data['monp2'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['monp2_col']) - 1], merge_row))
                data['moffp2'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['moffp2_col']) - 1], merge_row))
                data['mcp2'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['mcp2_col']) - 1],
                                       merge_row))
                data['mcl2'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['mcl2_col']) - 1],
                                       merge_row))
                data['mgp'] = sum(map(lambda i:
                                      cdf.loc[i - rbjsb_sheet['start_row']].values[
                                          column_index_from_string(rbjsb_sheet['mgp_col']) - 1],
                                      merge_row))
                data['monp'] = sum(map(lambda i:
                                       cdf.loc[i - rbjsb_sheet['start_row']].values[
                                           column_index_from_string(rbjsb_sheet['monp_col']) - 1],
                                       merge_row))
                data['moffp'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['moffp_col']) - 1], merge_row))
                data['mcp'] = sum(map(lambda i:
                                      cdf.loc[i - rbjsb_sheet['start_row']].values[
                                          column_index_from_string(rbjsb_sheet['mcp_col']) - 1],
                                      merge_row))
                data['mcl'] = sum(map(lambda i:
                                      cdf.loc[i - rbjsb_sheet['start_row']].values[
                                          column_index_from_string(rbjsb_sheet['mcl_col']) - 1],
                                      merge_row))
                data['offja311'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['doffja_311_col']) - 1], merge_row))
                data['offjr311'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['doffjr_311_col']) - 1], merge_row))
                data['offja321'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['doffja_321_col']) - 1], merge_row))
                data['offjr321'] = sum(map(lambda i: cdf.loc[i - rbjsb_sheet['start_row']].values[
                    column_index_from_string(rbjsb_sheet['doffjr_321_col']) - 1], merge_row))
                break
        if continue_flag == 1:
            # 出发flag，本次循环结束，不需要执行事务
            continue
        if CalDailyForm().getOne(CalDailyForm,
                                 {CalDailyForm.date == cdf.loc[x].values[0]}):
            # 如果数据库存在本日数据，更新数据
            CalDailyForm().update(data,
                                  {
                                      CalDailyForm.date == cdf.loc[x].values[0]
                                  }
                                  )
        else:
            CalDailyForm().add(data)
    return BaseController().successData(result=response, msg='日报表数据更新成功！')


def import_dlfs(dlfs_file, year, types='insert'):
    """
    自动化对每日电量风速统计表进行读取同步
    dlfs_file: 风机电量风速文件
    year: 数据年份
    types: insert 插入模式 / overwrite 覆盖模式
    """
    if str(year) in config.keys():
        cfg_dlfs = config[str(year)]['dlfs']
    else:
        cfg_dlfs = config['default']['dlfs']
    dlfs = pd.read_excel(dlfs_file if dlfs_file else os.path.join(cfg_dlfs['dir'], cfg_dlfs['name']),
                         sheet_name=cfg_dlfs['sheet0']['name'],
                         usecols=range(column_index_from_string(cfg_dlfs['sheet0']['end_col'])),
                         skiprows=range(cfg_dlfs['sheet0']['start_row'] - 1),
                         header=None
                         ).fillna(0)
    response = []
    for x in range(366):
        if types == 'insert' and CalDailyForm.query.filter_by(
                date=dlfs.loc[x].values[0]).first():
            continue  # 如果数据库存在本日数据，那么跳过
        data = {
            'davgs1': float(dlfs.loc[x].values[1]),
            'davgs2': float(dlfs.loc[x].values[2]),
            'davgs': float(Utils.realRound((float(dlfs.loc[x].values[1]) + float(dlfs.loc[x].values[2])) / 2, 2))
        }
        if pd.isnull(dlfs.loc[x].values[1]):
            # if cdf.loc[x].values[0] >= datetime.now():
            break  # 如果读到的数据不是浮点数类型，那么停止，用于判断是否到达表内空行
        if CalDailyForm().getOne(CalDailyForm,
                                 {CalDailyForm.date == dlfs.loc[x].values[0]}):
            CalDailyForm().edit(CalDailyForm, data,
                                {CalDailyForm.date == dlfs.loc[x].values[0]})
        else:
            CalDailyForm().add(data)
    return BaseController().successData(result=response, msg='风速数据更新成功！')


@app.route('/api/cdf', methods=['GET'])
def get_new_cdf():
    cdf = CalDailyForm().getNew()
    return BaseController().successData(result=cdf, msg='获取成功，数据时间为' + cdf['date'])


@app.route('/api/cdfs/days/<num>', methods=['GET'])
def get_cdfs(num):
    cdfs = CalDailyForm().getList({}, CalDailyForm.date.desc(), ('dgp', 'davgs', 'date', 'mgp', 'agp'), 0, int(num))[
        'list']
    newest_cdf = cdfs[0]
    newest_date = datetime.datetime.strptime(newest_cdf['date'], "%Y-%m-%d")
    year_rate = Utils.realRound(newest_cdf['agp'] / GpPlan.getGpPlan(newest_date.year) / 10000, 4)
    month_rate = Utils.realRound(newest_cdf['mgp'] / GpPlan.getGpPlan(newest_date.year, newest_date.month) / 10000, 4)
    plan_rate = Utils.realRound(
        GpPlan.getGpPlanUntil(newest_date.year, newest_date.month, newest_date.day) / GpPlan.getGpPlan(
            newest_date.year), 4)
    res = {
        'cdfs': cdfs,
        'year_rate': float(year_rate),
        'month_rate': float(month_rate),
        'plan_rate': float(plan_rate)
    }
    return BaseController().successData(result=res, msg='获取成功')


@app.route('/api/cdfs/timerange', methods=['POST'])
def get_cdfs_by_timerange():
    time_range = request.json.get('timeRange')
    today = datetime.datetime.now()
    if time_range == 'week':
        filters = {
            CalDailyForm.date >= today - datetime.timedelta(days=today.weekday()),
            CalDailyForm.date <= today + datetime.timedelta(days=6 - today.weekday())
        }
    # 今日为周一问题未解决
    elif time_range == 'month':
        pass
    elif time_range == 'year':
        pass
    else:
        pass
    result = CalDailyForm().getList(filters, CalDailyForm.date.desc(), ('dgp', 'davgs', 'date', 'mgp', 'agp'), 0, 31)[
        'list']
    return BaseController().successData(result=result, msg='获取成功')


@app.route('/api/gpplans', methods=['PUT'])
def get_gp_plans():
    """
    自动化对发电量计划进行读取
    """
    gpplan = pd.read_excel(r"C:\Users\admin\Desktop\1报表文件夹\日报表\2020年\山东分公司2020年发电量计划（2020.5调整版）.xlsx",
                           usecols=range(14), skiprows=range(1))
    gpplan.fillna(0)
    print(gpplan)
    year = 2020
    for x in range(40):
        if gpplan.loc[x].values[0] == '合计':
            break
        if gpplan.loc[x].values[0] == '石桥一期':
            for col_num in range(1, 13):
                gpp = GpPlan(year=year, month=col_num, num=1, plan_gp=int(gpplan.loc[x].values[col_num]))
                GpPlan().add(gpp)
        if gpplan.loc[x].values[0] == '石桥二期':
            for col_num in range(1, 13):
                gpp = GpPlan(year=year, month=col_num, num=2, plan_gp=int(gpplan.loc[x].values[col_num]))
                GpPlan().add(gpp)
    return BaseController().successData(msg='读取并写入成功！')
