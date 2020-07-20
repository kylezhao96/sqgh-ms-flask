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
from app.Vendor.Decorator import classTransaction


class WT(db.Model, BaseModel, SerializerMixin):
    __tablename__ = 'wts'
    wtm = db.relationship('WTMaintain', backref="wt", lazy='dynamic')
    id = db.Column(db.Integer, primary_key=True)
    line = db.Column(db.Integer)
    dcode = db.Column(db.Integer)
    type = db.Column(db.String(100), default='En121-2.5')

    def getDCode(self, wt_id):
        return db.session.query(WT).filter(WT.id == wt_id).first().dcode

    # 获取风机号
    @staticmethod
    def get(id):
        return db.session.query(WT).filter_by(id=id).first()
