import datetime

from dateutil.relativedelta import relativedelta
from flask import request

from app import app
from app.Controllers.BaseController import BaseController
from app.Models import CalDailyForm
import pandas as pd

from app.Models.GpPlan import GpPlan
from app.Vendor.Decorator import classTransaction
from app.env import EXCEL_PATH, TY_PATH
from app.Vendor.Utils import Utils


@app.route('/api/cdfs', methods=['PUT'])
def import_cdf():
    """
    自动化对日报表进行读取同步
    """
    cdf = pd.read_excel(EXCEL_PATH, sheet_name='日报计算表', usecols=range(76), skiprows=range(3), header=None)
    ty = pd.read_excel(TY_PATH, sheet_name='风速统计', usecols=range(3), skiprows=range(2), header=None).fillna('')
    cdf.fillna(0)
    print(cdf)
    response = []
    this_year = datetime.date.today().year
    for x in range(366):
        # if CalDailyForm.query.filter_by(date=cdf.loc[x + 1].values[0] + datetime.timedelta(-1)).first():
        # continue  # 如果数据库存在本日数据，那么跳过
        # cdf_db = CalDailyForm.query.filter_by(date=cdf.loc[x + 1].values[0] + datetime.timedelta(-1)).first()
        data = {}
        if x == 0:
            data['date'] = datetime.datetime(this_year - 1, 12, 31, 0, 0)
            data['fka312'] = float(cdf.loc[x].values[1])
            data['bka312'] = float(cdf.loc[x].values[2])
            data['fka313'] = float(cdf.loc[x].values[3])
            data['bka313'] = float(cdf.loc[x].values[4])
            data['fka322'] = float(cdf.loc[x].values[5])
            data['bka322'] = float(cdf.loc[x].values[6])
            data['fka323'] = float(cdf.loc[x].values[7])
            data['bka323'] = float(cdf.loc[x].values[8])
            data['fka31b'] = float(cdf.loc[x].values[9])
            data['fka21b'] = float(cdf.loc[x].values[10])
            data['fka311'] = float(cdf.loc[x].values[11])
            data['bka311'] = float(cdf.loc[x].values[12])
            data['fkr311'] = float(cdf.loc[x].values[13])
            data['bkr311'] = float(cdf.loc[x].values[14])
            data['fka321'] = float(cdf.loc[x].values[15])
            data['bka321'] = float(cdf.loc[x].values[16])
            data['fkr321'] = float(cdf.loc[x].values[17])
            data['bkr321'] = float(cdf.loc[x].values[18])
            data['bka111'] = float(cdf.loc[x].values[19])
            data['fka111'] = float(cdf.loc[x].values[20])
        else:
            if pd.isnull(cdf.loc[x].values[1]):
                # if cdf.loc[x].values[0] >= datetime.now():
                break  # 如果读到的数据不是浮点数类型，那么停止
            data['date'] = cdf.loc[x].values[0]
            data['fka312'] = float(cdf.loc[x].values[1])
            data['bka312'] = float(cdf.loc[x].values[2])
            data['fka313'] = float(cdf.loc[x].values[3])
            data['bka313'] = float(cdf.loc[x].values[4])
            data['fka322'] = float(cdf.loc[x].values[5])
            data['bka322'] = float(cdf.loc[x].values[6])
            data['fka323'] = float(cdf.loc[x].values[7])
            data['bka323'] = float(cdf.loc[x].values[8])
            data['fka31b'] = float(cdf.loc[x].values[9])
            data['fka21b'] = float(cdf.loc[x].values[10])
            data['fka311'] = float(cdf.loc[x].values[11])
            data['bka311'] = float(cdf.loc[x].values[12])
            data['fkr311'] = float(cdf.loc[x].values[13])
            data['bkr311'] = float(cdf.loc[x].values[14])
            data['fka321'] = float(cdf.loc[x].values[15])
            data['bka321'] = float(cdf.loc[x].values[16])
            data['fkr321'] = float(cdf.loc[x].values[17])
            data['bkr321'] = float(cdf.loc[x].values[18])
            data['bka111'] = float(cdf.loc[x].values[19])
            data['fka111'] = float(cdf.loc[x].values[20])
            data['dgp1'] = cdf.loc[x].values[21]
            data['donp1'] = cdf.loc[x].values[22]
            data['doffp1'] = cdf.loc[x].values[23]
            data['dcp1'] = cdf.loc[x].values[24]
            data['dcl1'] = cdf.loc[x].values[25]
            data['dgp2'] = cdf.loc[x].values[26]
            data['donp2'] = cdf.loc[x].values[27]
            data['doffp2'] = cdf.loc[x].values[28]
            data['dcp2'] = cdf.loc[x].values[29]
            data['dcl2'] = cdf.loc[x].values[30]
            data['dgp'] = cdf.loc[x].values[31]
            data['donp'] = cdf.loc[x].values[32]
            data['doffp'] = cdf.loc[x].values[33]
            data['dcp'] = cdf.loc[x].values[34]
            data['dcl'] = cdf.loc[x].values[35]
            data['doffp31b'] = cdf.loc[x].values[36]
            data['doffp21b'] = cdf.loc[x].values[37]
            data['agp1'] = cdf.loc[x].values[38]
            data['aonp1'] = cdf.loc[x].values[39]
            data['aoffp1'] = cdf.loc[x].values[40]
            data['acp1'] = cdf.loc[x].values[41]
            data['acl1'] = cdf.loc[x].values[42]
            data['agp2'] = cdf.loc[x].values[43]
            data['aonp2'] = cdf.loc[x].values[44]
            data['aoffp2'] = cdf.loc[x].values[45]
            data['acp2'] = cdf.loc[x].values[46]
            data['acl2'] = cdf.loc[x].values[47]
            data['agp'] = cdf.loc[x].values[48]
            data['aonp'] = cdf.loc[x].values[49]
            data['aoffp'] = cdf.loc[x].values[50]
            data['acp'] = cdf.loc[x].values[51]
            data['acl'] = cdf.loc[x].values[52]
            data['mgp1'] = cdf.loc[x].values[53]
            data['monp1'] = cdf.loc[x].values[54]
            data['moffp1'] = cdf.loc[x].values[55]
            data['mcp1'] = cdf.loc[x].values[56]
            data['mcl1'] = cdf.loc[x].values[57]
            data['mgp2'] = cdf.loc[x].values[58]
            data['monp2'] = cdf.loc[x].values[59]
            data['moffp2'] = cdf.loc[x].values[60]
            data['mcp2'] = cdf.loc[x].values[61]
            data['mcl2'] = cdf.loc[x].values[62]
            data['mgp'] = cdf.loc[x].values[63]
            data['monp'] = cdf.loc[x].values[64]
            data['moffp'] = cdf.loc[x].values[65]
            data['mcp'] = cdf.loc[x].values[66]
            data['mcl'] = cdf.loc[x].values[67]
            data['offja311'] = cdf.loc[x].values[69]
            data['offjr311'] = cdf.loc[x].values[71]
            data['offja321'] = cdf.loc[x].values[73]
            data['offjr321'] = cdf.loc[x].values[75]
            data['davgs1'] = float(ty.loc[x - 1].values[1])
            data['davgs2'] = float(ty.loc[x - 1].values[2])
            data['davgs'] = float(Utils.realRound((data['davgs1'] + data['davgs2']) / 2, 2))
        if CalDailyForm().getOne(CalDailyForm,
                                 {CalDailyForm.date == cdf.loc[x + 1].values[0] + datetime.timedelta(-1)}):
            # continue  # 如果数据库存在本日数据，那么跳过
            CalDailyForm().edit(CalDailyForm, data,
                                {CalDailyForm.date == cdf.loc[x + 1].values[0] + datetime.timedelta(-1)})
        else:
            CalDailyForm().add(data)
    return BaseController().successData(result=response, msg='日报表数据更新成功')


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
