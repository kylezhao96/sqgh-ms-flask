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
from app.Models.Model import HtCalDailyForm
from app import db
from app.Vendor.Decorator import classTransaction


class CalDailyForm(HtCalDailyForm, BaseModel, SerializerMixin):

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
