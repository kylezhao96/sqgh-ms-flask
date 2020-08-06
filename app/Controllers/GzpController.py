import datetime
import os
import re
import requests

from dateutil.relativedelta import relativedelta
from flask import request
from sqlalchemy import and_
from functools import reduce

from app import app
from app.Controllers.BaseController import BaseController
from app.Models import Gzp, WTMaintain, User, WT
from app.Vendor.Utils import Utils
import pandas as pd
import xlrd, xlutils, xlwt
from xlutils.copy import copy

from app.Vendor.Decorator import classTransaction
from app.env import EXCEL_PATH, TY_PATH, DESK_PATH
from app.Vendor.Utils import Utils


@app.route('/api/gzps/today', methods=['GET'])
def get_gzps_today():
    """
    读取今日工作票
    """
    # test_date = datetime.date(2020,1,1)
    gzps = Gzp().getList(
        {Gzp.pstart_time >= datetime.date.today()},
        Gzp.pstart_time.desc(),
        ('gzp_id', 'manager', 'date', 'mgp', 'agp')
    )
    # gzps = Gzp().getGzpList(0, 10)
    gzps_list = gzps['list']
    data = []
    for item in gzps_list:
        members = ''
        for member in item['members']:
            members = members + member['name'] + '，'
        members = members[:-1]
        wts = ''
        wtms = list()
        index = 0
        for wt_id in item['wts']:
            wtms.append({})
            if len(list(filter(lambda x: x['wt_id'] == wt_id, item['wtms']))):
                wtm = list(filter(lambda x: x['wt_id'] == wt_id, item['wtms']))[0]
                wtms[index] = {
                    'wt_id': wt_id,
                    'stop_time': datetime.datetime.strftime(wtm['stop_time'], '%Y-%m-%d %H:%M'),
                    'start_time': '' if not wtm['start_time'] else datetime.datetime.strftime(wtm['start_time'],
                                                                                              '%Y-%m-%d %H:%M'),
                    'lost_power': wtm['lost_power'],
                    'time': wtm['time']
                }
            else:
                wtms[index] = {
                    'wt_id': wt_id,
                    'stop_time': '',
                    'start_time': '',
                    'lost_power': '',
                    'time': ''
                }
            wts = wts + 'A' + str(wt_id) + '，'
            index = index + 1
        wts = wts[:-1]
        x = {
            'id': item['gzp_id'],
            'wt_id': wts,
            'manager': User().get(item['manage_person_id']).name,
            'task': item['task'],
            'members': members,
            'pstart_time': datetime.datetime.strftime(item['pstart_time'], '%Y-%m-%d %H:%M'),
            'pstop_time': datetime.datetime.strftime(item['pstop_time'], '%Y-%m-%d %H:%M'),
            'wtms': wtms,
            'is_end': item['is_end'],
        }
        if item['error_code']:
            x['error_code'] = item['error_code']
        data.append(x)
        # index = index + 1
    print(data)
    return BaseController().successData(result=data, msg='工作票读取成功')


@app.route('/api/syn/wtm', methods=['PUT'])
def wtm_syn():
    res = gzp_syn()  # 现将工作票同步
    whtj = pd.read_excel(EXCEL_PATH, sheet_name='风机维护统计',
                         usecols=range(20), header=None).fillna('')
    gztj = pd.read_excel(EXCEL_PATH, sheet_name='风机故障统计',
                         usecols=range(20), header=None).fillna('')
    # 维护
    for x in range(len(whtj)):
        if re.findall(r'^(A)(\d+)(\s*)(\d{5})$', whtj.loc[x].values[0]):
            stop_time = whtj.loc[x].values[3]
            zero_time = stop_time - datetime.timedelta(hours=stop_time.hour, minutes=stop_time.minute,
                                                       seconds=stop_time.second)
            wt_id = int(re.match(r'^(A)(\d+)(\s*)(\d{5})$', whtj.loc[x].values[0]).group(2))
            try:
                gzp = Gzp.query.filter(
                    and_(Gzp.pstart_time < stop_time, Gzp.pstart_time > zero_time,
                         Gzp.wts.any(id=wt_id))).first()  # 这里可能会生成bug
                wtm = WTMaintain()
                is_in = False
                for item in gzp.wtms:
                    if item == WTMaintain.query.filter(WTMaintain.stop_time == whtj.loc[x].values[3],
                                                       WTMaintain.start_time == whtj.loc[x].values[4]).first():
                        wtm = item
                        is_in = True  # 标定数据库中已存在
                wtm.wt_id = wt_id
                wtm.type = whtj.loc[x].values[1]
                wtm.task = whtj.loc[x].values[2]
                wtm.stop_time = whtj.loc[x].values[3]
                wtm.start_time = whtj.loc[x].values[4]
                wtm.time = Utils.realRound(
                    (wtm.start_time - wtm.stop_time).seconds / 3600, 2)
                wtm.lost_power = Utils.realRound(float(whtj.loc[x].values[6]), 4)
                if not is_in:
                    gzp.wtms.append(wtm)
                if len(gzp.wtms.all()) == len(gzp.wts.all()):
                    gzp.is_end = 1
                Gzp().add(gzp)
            except(AttributeError):
                print('工作票不存在，风机号：A' + str(wt_id) + '，停机时间' + str(stop_time))
                res.append('风机号：A' + str(wt_id) + '，停机时间' + str(stop_time))
        if re.findall(r'^(A)(\d+)(\s*)(\d{5})$', whtj.loc[x].values[8]):
            stop_time = whtj.loc[x].values[11]
            zero_time = stop_time - datetime.timedelta(hours=stop_time.hour, minutes=stop_time.minute,
                                                       seconds=stop_time.second)
            wt_id = int(re.match(r'^(A)(\d+)(\s*)(\d{5})$', whtj.loc[x].values[8]).group(2))
            try:
                gzp = Gzp.query.filter(
                    and_(Gzp.pstart_time < stop_time, Gzp.pstart_time > zero_time,
                         Gzp.wts.any(id=wt_id))).first()  # 这里可能会生成bug
                wtm = WTMaintain()
                is_in = False
                for item in gzp.wtms:
                    if item == WTMaintain.query.filter(WTMaintain.stop_time == whtj.loc[x].values[11],
                                                       WTMaintain.start_time == whtj.loc[x].values[12]).first():
                        wtm = item
                        is_in = True  # 标定数据库中已存在
                wtm.wt_id = wt_id
                wtm.type = whtj.loc[x].values[9]
                wtm.task = whtj.loc[x].values[10]
                wtm.stop_time = whtj.loc[x].values[11]
                wtm.start_time = whtj.loc[x].values[12]
                wtm.time = Utils.realRound(
                    (wtm.start_time - wtm.stop_time).seconds / 3600, 2)
                wtm.lost_power = Utils.realRound(float(whtj.loc[x].values[13]), 4)
                if not is_in:
                    gzp.wtms.append(wtm)
                if len(gzp.wtms.all()) == len(gzp.wts.all()):
                    gzp.is_end = 1
                Gzp().add(gzp)
            except(AttributeError):
                print('工作票不存在，风机号：A' + str(wt_id) + '，停机时间' + str(stop_time))
                res.append('风机号：A' + str(wt_id) + '，停机时间' + str(stop_time))
    # 故障
    for x in range(len(gztj)):
        if re.findall(r'^(A)(\d+)(\s*)(\d{5})$', gztj.loc[x].values[0]):
            stop_time = gztj.loc[x].values[4]
            start_time = gztj.loc[x].values[5]
            if stop_time.hour < 18:
                zero_time = stop_time - datetime.timedelta(hours=stop_time.hour, minutes=stop_time.minute,
                                                           seconds=stop_time.second) + datetime.timedelta(days=1)
            else:
                zero_time = stop_time - datetime.timedelta(hours=stop_time.hour, minutes=stop_time.minute,
                                                           seconds=stop_time.second) + datetime.timedelta(days=2)
            wt_id = int(re.match(r'^(A)(\d+)(\s*)(\d{5})$', gztj.loc[x].values[0]).group(2))
            try:
                gzp = Gzp.query.filter(
                    and_(Gzp.pstart_time > stop_time, Gzp.pstart_time < zero_time,
                         Gzp.wts.any(id=wt_id))).first()  # 这里可能会生成bug
                wtm = WTMaintain()
                is_in = False
                for item in gzp.wtms:
                    if item == WTMaintain.query.filter(WTMaintain.stop_time == stop_time,
                                                       WTMaintain.start_time == start_time).first():
                        wtm = item
                        is_in = True  # 标定数据库中已存在
                wtm.wt_id = wt_id
                wtm.error_code = gztj.loc[x].values[1]
                wtm.error_content = gztj.loc[x].values[2]
                wtm.type = gztj.loc[x].values[3]
                wtm.stop_time = gztj.loc[x].values[4]
                wtm.start_time = gztj.loc[x].values[5]
                wtm.time = Utils.realRound(
                    (wtm.start_time - wtm.stop_time).seconds / 3600, 2)
                wtm.lost_power = Utils.realRound(float(gztj.loc[x].values[7]), 4)
                wtm.error_approach = gztj.loc[x].values[8]
                wtm.task = gzp.task
                if not is_in:
                    gzp.wtms.append(wtm)
                if len(gzp.wtms.all()) == len(gzp.wts.all()):
                    gzp.is_end = 1
                Gzp().add(gzp)
            except(AttributeError):
                print('工作票不存在，风机号：A' + str(wt_id) + '，停机时间' + str(stop_time))
                res.append('风机号：A' + str(wt_id) + '，停机时间' + str(stop_time))
        if re.findall(r'^(A)(\d+)(\s*)(\d{5})$', gztj.loc[x].values[10]):
            stop_time = gztj.loc[x].values[14]
            start_time = gztj.loc[x].values[15]
            if stop_time.hour < 18:
                zero_time = stop_time - datetime.timedelta(hours=stop_time.hour, minutes=stop_time.minute,
                                                           seconds=stop_time.second) + datetime.timedelta(days=1)
            else:
                zero_time = stop_time - datetime.timedelta(hours=stop_time.hour, minutes=stop_time.minute,
                                                           seconds=stop_time.second) + datetime.timedelta(days=2)
            wt_id = int(re.match(r'^(A)(\d+)(\s*)(\d{5})$', gztj.loc[x].values[10]).group(2))
            try:
                gzp = Gzp.query.filter(
                    and_(Gzp.pstart_time > stop_time, Gzp.pstart_time < zero_time,
                         Gzp.wts.any(id=wt_id))).first()  # 这里可能会生成bug
                wtm = WTMaintain()
                is_in = False
                for item in gzp.wtms:
                    if item == WTMaintain.query.filter(WTMaintain.stop_time == stop_time,
                                                       WTMaintain.start_time == start_time).first():
                        wtm = item
                        is_in = True  # 标定数据库中已存在
                wtm.wt_id = wt_id
                wtm.error_code = gztj.loc[x].values[11]
                wtm.error_content = gztj.loc[x].values[12]
                wtm.type = gztj.loc[x].values[13]
                wtm.stop_time = gztj.loc[x].values[14]
                wtm.start_time = gztj.loc[x].values[15]
                wtm.time = Utils.realRound(
                    (wtm.start_time - wtm.stop_time).seconds / 3600, 2)
                wtm.lost_power = Utils.realRound(float(gztj.loc[x].values[17]), 4)
                wtm.error_approach = gztj.loc[x].values[18]
                wtm.task = gzp.task
                if not is_in:
                    gzp.wtms.append(wtm)
                if len(gzp.wtms.all()) == len(gzp.wts.all()):
                    gzp.is_end = 1
                Gzp().add(gzp)
            except(AttributeError):
                print('工作票不存在，风机号：A' + str(wt_id) + '，停机时间' + str(stop_time))
                res.append('风机号：A' + str(wt_id) + '，停机时间' + str(stop_time))
    return BaseController().successData(msg='res')


def gzp_syn():
    res = []
    path = DESK_PATH + r'\5OA系统风机工作票'
    for year_folder in os.listdir(path):
        if re.match('\d+年$', year_folder):
            for month_folder in os.listdir(path + '\\' + year_folder):
                if re.match('\d+月$', month_folder):
                    for gzp in os.listdir(path + '\\' + year_folder + '\\' + month_folder):
                        if re.match(r'^(风机检修工作票)\S+(\.xls)$', gzp):
                            data_gzp = pd.read_excel(
                                path + '\\' + year_folder + '\\' + month_folder + '\\' + gzp)  # 读取
                            # if not Gzp.query.filter_by(gzp_id=data_gzp.loc[1].values[13]).first():
                            if not Gzp.get(data_gzp.loc[1].values[13]):
                                gzp = Gzp()
                            else:
                                gzp = Gzp.get(data_gzp.loc[1].values[13])
                            gzp.firm = data_gzp.loc[1].values[1]
                            # 以下开始对各项数据进行读取
                            for index, row in data_gzp.fillna('').iterrows():
                                for col_num in range(0, 19):
                                    if row.values[col_num] != '' and isinstance(row.values[col_num], str):
                                        # 匹配编号
                                        if re.match(r'\S{4}-\S{2}-\S{2}-\d{9}', row.values[col_num]):
                                            gzp.gzp_id = re.match(r'\S{4}-\S{2}-\S{2}-\d{9}',
                                                                  row.values[col_num]).group()
                                        # 匹配工作负责人
                                        if row.values[col_num] == '1、工作负责人(监护人)':
                                            gzp.manage_person = User().getByName(row.values[col_num + 4])
                                        # 匹配工作班成员
                                        if row.values[col_num] == '2、工作班成员（不包括工作负责人）':
                                            members = re.split(
                                                "\W+", data_gzp.loc[index + 1].values[0].strip())
                                            members_temp = []
                                            for member in members:
                                                members_temp.append(User().getByName(member))
                                            gzp.members = members_temp
                                        # 匹配故障
                                        if row.values[col_num] == '3、工作任务':
                                            if isinstance(data_gzp.loc[index + 1].values[5], str):
                                                if re.match(r'(SC\d+_\d+_\d+)\\?(\w+)?',
                                                            data_gzp.loc[index + 1].values[5]):
                                                    gzp.error_code = re.match(
                                                        r'(SC\d+_\d+_\d+)\\?(\w+)?',
                                                        data_gzp.loc[index + 1].values[5]).group(1)
                                                    if re.match(r'(SC\d+_\d+_\d+)\\?(\w+)?',
                                                                data_gzp.loc[index + 1].values[5]).group(2):
                                                        gzp.error_content = re.match(
                                                            r'(SC\d+_\d+_\d+)\\?(\w+)?',
                                                            data_gzp.loc[index + 1].values[5]).group(2)
                                                    else:
                                                        gzp.error_content = re.match(
                                                            r'(处理)?(\w+)', data_gzp.loc[index + 3].values[10]).group(2)
                                            # 匹配风机
                                            gzp_wts_id = list(
                                                map(lambda x: re.match(r'^(A)(\d+)$', x).group(2),
                                                    re.findall(re.compile(r'A\d+'), data_gzp.loc[index + 3].values[0])))
                                            gzp.wts = list(map(lambda x: WT.get(int(x)), gzp_wts_id))  # wt放在最后
                                            gzp.postion = data_gzp.loc[index + 3].values[5]
                                            gzp.task = data_gzp.loc[index + 3].values[10]
                                        # 匹配时间
                                        if row.values[col_num] == '5、计划工作时间':
                                            try:
                                                gzp.pstart_time = datetime.datetime(data_gzp.loc[index + 1].values[2],
                                                                                    data_gzp.loc[index + 1].values[4],
                                                                                    data_gzp.loc[index + 1].values[6],
                                                                                    data_gzp.loc[index + 1].values[8],
                                                                                    data_gzp.loc[index + 1].values[10])
                                                now = datetime.datetime.now()
                                                zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute,
                                                                                     seconds=now.second,
                                                                                     microseconds=now.microsecond)

                                                if gzp.pstart_time < zeroToday:
                                                    gzp.is_end = 1  # 读取到非今日工作票记为已终结
                                                if data_gzp.loc[index + 2].values[8] != 24:
                                                    gzp.pstop_time = datetime.datetime(
                                                        data_gzp.loc[index + 2].values[2],
                                                        data_gzp.loc[index + 2].values[4],
                                                        data_gzp.loc[index + 2].values[6],
                                                        data_gzp.loc[index + 2].values[8],
                                                        data_gzp.loc[index + 2].values[10])
                                                else:
                                                    gzp.pstop_time = datetime.datetime(
                                                        data_gzp.loc[index + 2].values[2],
                                                        data_gzp.loc[index + 2].values[4],
                                                        data_gzp.loc[index + 2].values[6], 0,
                                                        data_gzp.loc[index + 2].values[10]) + datetime.timedelta(days=1)
                                            except ValueError:
                                                res.append(gzp.gzp_id)
                                                print(gzp.gzp_id)
                            Gzp().add(gzp)
    return res


@app.route('/api/firms', methods=['POST'])
def get_firms_today():
    parms = request.get_json() or ''
    filters = {}
    if parms:
        filters = {
            Gzp.firm.contains(parms['value'])
        }
    resList = Gzp().getFirmList(filters)
    if not len(resList):
        resList.append(parms['value'])
    return BaseController().successData(result=resList)


@app.route('/api/gzp/id/new', methods=['GET'])
def get_new_gzp_id():
    gzp_id_max = Gzp().getList({}, Gzp.gzp_id.desc(), ('gzp_id',), 0, 1)['list'][0]['gzp_id']
    matchObj = re.search(r"(\d{4})(\d{2})(\d{3})", gzp_id_max)
    year = int(matchObj.group(1))
    month = int(matchObj.group(2))
    id = int(matchObj.group(3))
    today = datetime.date.today()
    if year != today.year or month != today.month:
        id = 1
    else:
        id = id + 1
    res = {
        'gzp_id': 'FJGZ-SD-SQ' + str(today.year).zfill(4) + str(today.month).zfill(2) + str(id).zfill(3),
        'gzp_id_num': str(today.year).zfill(4) + str(today.month).zfill(2) + str(id).zfill(3)
    }
    return BaseController().successData(result=res)


@app.route('/api/gzp/new', methods=['POST'])
def submitGzpform():
    form = request.get_json() or ''
    df = pd.read_excel(os.getcwd() + r'\template\风机检修工作票模板.xls', header=None)
    wb = xlrd.open_workbook(os.getcwd() + r'\template\风机检修工作票模板.xls', formatting_info=True)
    ws = wb.sheet_by_index(0)

    # 格式设定
    # 设置字体
    font = xlwt.Font()
    # 字体类型
    font.name = '宋体'
    # 字体大小，11为字号，20为衡量单位
    font.height = 20 * 9
    # 设置单元格对齐方式
    alignment_center = xlwt.Alignment()
    alignment_left = xlwt.Alignment()
    # 0x01(左端对齐)、0x02(水平方向上居中对齐)、0x03(右端对齐)
    alignment_center.horz = 0x02
    alignment_left.horz = 0x01
    # 设置边框
    borders = xlwt.Borders()
    borders.bottom = 1

    # 样式1
    style0 = xlwt.XFStyle()
    style0.font = font
    style0.alignment = alignment_center
    style0.borders = borders

    # 样式2 左对齐
    style1 = xlwt.XFStyle()
    style1.font = font
    style1.borders = borders
    style1.alignment = alignment_left

    # 复制
    new_wb = copy(wb)
    new_ws = new_wb.get_sheet(0)

    # 写入
    new_ws.write(2, 13, 'FJGZ-SD-SQ-' + form['gzpId'], style0)
    new_ws.write(2, 1, form['firm']['key'], style0)
    new_ws.write(4, 11, form['group'], style0)
    new_ws.write(4, 4, form['manager']['key'], style0)
    if len(form['members']) > 1:
        new_ws.write(7, 0, reduce(lambda x, y: x + '、' + y, map(lambda x: x['key'], form['members'])), style1)
    else:
        new_ws.write(7, 0, form['members']['key'], style1)
    new_ws.write(7, 16, len(form['members']) + 1, style0)
    new_ws.write(14,0,'机组'+ form['terminalWt']+'/'+'机组'+form['terminalPower'])
    new_wb.save(os.getcwd() + r'\template\风机检修工作票模板1.xls')
    return BaseController().successData(msg='成功')


@app.route('/api/gzp/weather/now', methods=['GET'])
def get_weather_now():
    res = requests.get('https://free-api.heweather.com/s6/weather/now?location=119.238801,36.09725&key=c4a0db75e5234137a88df8eccbcc7fe4').json()
    return BaseController().successData(result={
        'tmp': res['HeWeather6'][0]['now']['tmp'],
        'cond_txt': res['HeWeather6'][0]['now']['cond_txt'],
        'wind_spd': float(Utils.realRound(int(res['HeWeather6'][0]['now']['wind_spd']) / 3.6, 1))
    })
