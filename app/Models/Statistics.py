"""
@Author: kyle
@Date: 2020-06-19 20:56
@description:
@LastEditors: kyle
@LastEditTime: 2020-06-19 20:56
"""

from sqlalchemy import desc, asc
from sqlalchemy_serializer import SerializerMixin

from app.Models.BaseModel import BaseModel
from app import db
from app.Models.Model import statistics_wtm
from app.Vendor.Decorator import classTransaction


class Statistics(db.Model, BaseModel, SerializerMixin):
    __tablename__ = 'statistics'
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(100), unique=True)
    wtms = db.relationship("WTMaintain", secondary=statistics_wtm, backref=db.backref('statistics', lazy='dynamic'),
                              lazy="dynamic")  # 工作班成员
    completed = db.Column(db.Boolean, default=False)

    def to_dict(self, only=()):
        resp_dict = {
            'id': self.id,
            'task': self.task,
            'wtms': [{'id': x.id, 'task': x.name, 'wt_id': x.wt_id, 'gzp_id': x.gzp_id} for x in self.wtms]
        }
        if only:
            resp_dict = {k: v for k, v in resp_dict.items() if k in only}
        return resp_dict

    def getList(self, filters, order: str = "id desc", field=()):
        """
            列表
            @param set filters 查询条件
            @param obj order 排序
            @param tuple field 字段
            @return dict
        """
        res = db.session.query(Statistics).filter(*filters)
        orderArr = order.split(' ')
        if orderArr[1] == 'desc':
            res = res.order_by(desc(orderArr[0])).all()
        else:
            res = res.order_by(asc(orderArr[0])).all()
        if not field:
            res = [c.to_dict() for c in res]
        else:
            res = [c.to_dict(only=field) for c in res]
        return res
