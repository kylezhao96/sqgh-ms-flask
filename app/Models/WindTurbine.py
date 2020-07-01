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
from app.Models.Model import HtWt
from app import db
from app.Vendor.Decorator import classTransaction


class WT(HtWt, BaseModel, SerializerMixin):
    def getDCode(self, wt_id):
        return db.session.query(WT).filter(WT.id == wt_id).first().dcode
