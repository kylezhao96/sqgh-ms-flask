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


class PowerCut(db.Model, BaseModel, SerializerMixin):
    __tablename__ = 'powercuts'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)  # 限电开始时间
    stop_time = db.Column(db.DateTime)  # 限电结束时间
    time = db.Column(db.Float)  # 限电时间
    lost_power1 = db.Column(db.Float)  # 1期损失电量
    lost_power2 = db.Column(db.Float)  # 2期损失电量
