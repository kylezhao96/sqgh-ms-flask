'''
@Author: hua
@Date: 2018-08-30 10:52:23
@description: 
@LastEditors: hua
@LastEditTime: 2019-12-03 14:08:27
'''
from app import db
from sqlalchemy import desc, asc, Column, Integer, FetchedValue, Text
from app.Models.BaseModel import BaseModel
from app.Models.Model import HtLog
from sqlalchemy_serializer import SerializerMixin
from app.Vendor.Decorator import classTransaction


class Log(HtLog, BaseModel, SerializerMixin):

    def getOne(self, filters, order='id desc', field=()):
        res = db.session.query(Log).filter(*filters)
        order = order.split(' ')
        if order[1] == 'desc':
            res = res.order_by(desc(order[0])).first()
        else:
            res = res.order_by(asc(order[0])).first()
        if res == None:
            return None
        if not field:
            res = res.to_dict()
        else:
            res = res.to_dict(only=field)
        return res

    """
        添加
        @param obj data 数据
        @return bool
    """

    @classTransaction
    def add(self, data):
        log = Log(**data)
        db.session.add(log)
        db.session.flush()
        return log.id
