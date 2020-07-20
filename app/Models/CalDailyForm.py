"""
@Author: kyle
@Date: 2020-06-19 20:56
@description:
@LastEditors: kyle
@LastEditTime: 2020-06-19 20:56
"""
import math

from sqlalchemy import desc, asc
from sqlalchemy.orm import session
from sqlalchemy_serializer import SerializerMixin

from app.Models.BaseModel import BaseModel
from app import db
from app.Vendor.Decorator import classTransaction


class CalDailyForm(db.Model, BaseModel, SerializerMixin):
    __tablename__ = 'cdfs'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True)
    # ka有功 kr有功 f正向 b反向
    fka312 = db.Column(db.Float)
    bka312 = db.Column(db.Float)
    fka313 = db.Column(db.Float)
    bka313 = db.Column(db.Float)
    fka322 = db.Column(db.Float)
    bka322 = db.Column(db.Float)
    fka323 = db.Column(db.Float)
    bka323 = db.Column(db.Float)
    fka31b = db.Column(db.Float)
    fka21b = db.Column(db.Float)
    fka311 = db.Column(db.Float, default=0)
    bka311 = db.Column(db.Float)
    fkr311 = db.Column(db.Float, default=0)
    bkr311 = db.Column(db.Float)
    fka321 = db.Column(db.Float, default=0)
    bka321 = db.Column(db.Float)
    fkr321 = db.Column(db.Float, default=0)
    bkr321 = db.Column(db.Float)
    bka111 = db.Column(db.Float)
    fka111 = db.Column(db.Float)
    # p 发电量 d 每日的 g总的 on上网的 off下网的 c场用的 l率
    dgp1 = db.Column(db.Integer)
    donp1 = db.Column(db.Integer)
    doffp1 = db.Column(db.Integer)
    dcp1 = db.Column(db.Integer)
    dcl1 = db.Column(db.Float)
    dgp2 = db.Column(db.Integer)
    donp2 = db.Column(db.Integer)
    doffp2 = db.Column(db.Integer)
    dcp2 = db.Column(db.Integer)
    dcl2 = db.Column(db.Float)
    dgp = db.Column(db.Integer)
    donp = db.Column(db.Integer)
    doffp = db.Column(db.Integer)
    dcp = db.Column(db.Integer)
    dcl = db.Column(db.Float)
    doffp31b = db.Column(db.Integer)
    doffp21b = db.Column(db.Integer)
    # 年的
    agp1 = db.Column(db.Integer)
    aonp1 = db.Column(db.Integer)
    aoffp1 = db.Column(db.Integer)
    acp1 = db.Column(db.Integer)
    acl1 = db.Column(db.Float)
    agp2 = db.Column(db.Integer)
    aonp2 = db.Column(db.Integer)
    aoffp2 = db.Column(db.Integer)
    acp2 = db.Column(db.Integer)
    acl2 = db.Column(db.Float)
    agp = db.Column(db.Integer)
    aonp = db.Column(db.Integer)
    aoffp = db.Column(db.Integer)
    acp = db.Column(db.Integer)
    acl = db.Column(db.Float)
    # 月的
    mgp1 = db.Column(db.Integer)
    monp1 = db.Column(db.Integer)
    moffp1 = db.Column(db.Integer)
    mcp1 = db.Column(db.Integer)
    mcl1 = db.Column(db.Float)
    mgp2 = db.Column(db.Integer)
    monp2 = db.Column(db.Integer)
    moffp2 = db.Column(db.Integer)
    mcp2 = db.Column(db.Integer)
    mcl2 = db.Column(db.Float)
    mgp = db.Column(db.Integer)
    monp = db.Column(db.Integer)
    moffp = db.Column(db.Integer)
    mcp = db.Column(db.Integer)
    mcl = db.Column(db.Float)
    # svg ja有功功率 jr无功功率
    offja311 = db.Column(db.Integer)
    offjr311 = db.Column(db.Integer)
    offja321 = db.Column(db.Integer)
    offjr321 = db.Column(db.Integer)
    # s 风速
    dmaxs = db.Column(db.Float)
    dmins = db.Column(db.Float)
    davgs = db.Column(db.Float)
    dmaxs1 = db.Column(db.Float)
    dmins1 = db.Column(db.Float)
    davgs1 = db.Column(db.Float)
    dmaxs2 = db.Column(db.Float)
    dmins2 = db.Column(db.Float)
    davgs2 = db.Column(db.Float)
    # lp 限电
    dlp1 = db.Column(db.Float, default=0)  # 一期日限电量
    dlp2 = db.Column(db.Float, default=0)  # 二期日限电量
    dlp = db.Column(db.Float, default=0)  # 总日限电量
    mlp1 = db.Column(db.Float, default=0)  # 一期月限电量
    mlp2 = db.Column(db.Float, default=0)  # 二期月限电量
    mlp = db.Column(db.Float, default=0)  # 总月限电量
    alp1 = db.Column(db.Float, default=0)  # 一期年限电量
    alp2 = db.Column(db.Float, default=0)  # 二期年限电量
    alp = db.Column(db.Float, default=0)  # 总年限电量
    # l 负荷
    dmaxl = db.Column(db.Float)  # 日最大负荷
    dminl = db.Column(db.Float)  # 日最小负荷
    def getNew(self):
        data = db.session.query(CalDailyForm).order_by(CalDailyForm.id.desc()).first().to_dict()
        return data


    def getOneByDate(self, date):
        filters = {
            CalDailyForm.date == date
        }
        data = self().getOne(CalDailyForm, filters, 'date desc')
        return data

    def getCdfList(self, page, per_page):
        data = self.getList({}, CalDailyForm.date.desc(), (), page, per_page)
        return data

    def getList(self, filters, order, field=(), offset=0, limit=15):
        res = {}
        res['page'] = {}
        res['page']['count'] = db.session.query(CalDailyForm).filter(*filters).count()
        res['list'] = []
        res['page']['total_page'] = self.get_page_number(res['page']['count'], limit)
        res['page']['current_page'] = offset
        if offset != 0:
            offset = (offset - 1) * limit
        if res['page']['count'] > 0:
            res['list'] = db.session.query(CalDailyForm).filter(*filters)
            res['list'] = res['list'].order_by(order).offset(offset).limit(limit).all()
        if not field:
            res['list'] = [c.to_dict() for c in res['list']]
        else:
            res['list'] = [c.to_dict(only=field) for c in res['list']]
        return res

    @staticmethod
    def get_page_number(count, page_size):
        count = float(count)
        page_size = abs(page_size)
        if page_size != 0:
            total_page = math.ceil(count / page_size)
        else:
            total_page = math.ceil(count / 5)
        return total_page

    @classTransaction
    def add(self, cdf_dict):
        cdf = CalDailyForm(**cdf_dict)
        db.session.add(cdf)
        return True
