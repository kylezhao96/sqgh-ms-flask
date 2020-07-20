"""
@Author: kyle
@Date: 2020-06-19 20:56
@description:
@LastEditors: kyle
@LastEditTime: 2020-06-19 20:56
"""
import math

from sqlalchemy import desc, asc
from sqlalchemy_serializer import SerializerMixin

from app.Models.BaseModel import BaseModel
from app import db


class WTMaintain(db.Model, BaseModel, SerializerMixin):
    __tablename__ = 'wtms'
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(100))  # 工作内容
    stop_time = db.Column(db.DateTime)  # 停机时间
    start_time = db.Column(db.DateTime)  # 启机时间
    lost_power = db.Column(db.Float)  # 损失电量
    time = db.Column(db.Float)  # 停机时间
    error_code = db.Column(db.String(100))
    error_content = db.Column(db.String(100))
    type = db.Column(db.String(100))
    error_approach = db.Column(db.String(100))

    wt_id = db.Column(db.Integer, db.ForeignKey('wts.id'))
    gzp_id = db.Column(db.String(50), db.ForeignKey('gzps.gzp_id', ondelete="CASCADE"))  # 定义关系工作票与维护单

    def getWtmList(self, page, per_page):
        data = self.getList(WTMaintain, {}, "id desc", (), page, per_page)
        return data
