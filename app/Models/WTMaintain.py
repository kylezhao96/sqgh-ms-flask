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
from app.Models.Model import HtWTMaintain
from app import db


class WTMaintain(HtWTMaintain, BaseModel, SerializerMixin):

    def getWtmList(self, page, per_page):
        data = self.getList(WTMaintain, {}, "id desc", (), page, per_page)
        return data
