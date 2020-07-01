"""
@Author: kyle
@Date: 2020-06-19 20:56
@description:
@LastEditors: kyle
@LastEditTime: 2020-06-19 20:56
"""
import math

from sqlalchemy import desc, asc, Integer, Column, ForeignKey, DateTime, String, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy_serializer import SerializerMixin

from app.Models import User
from app.Models.BaseModel import BaseModel
from app.Models.Model import HtGzp
from app import db
from app.Vendor.Decorator import classTransaction


class Gzp(HtGzp, BaseModel, SerializerMixin):

    def getGzpList(self, page, per_page):

        data = self.getList({}, Gzp.pstart_time.desc(), (), page, per_page)

        return data

    """ 
        列表
        @param set filters 查询条件
        @param obj order 排序
        @param tuple field 字段
        @param int offset 偏移量
        @param int limit 取多少条
        @return dict
    """

    def getList(self, filters, order, field=(), offset=0, limit=15):
        res = {}
        res['page'] = {}
        res['page']['count'] = db.session.query(Gzp).filter(*filters).count()
        res['list'] = []
        res['page']['total_page'] = self.get_page_number(res['page']['count'], limit)
        res['page']['current_page'] = offset
        if offset != 0:
            offset = (offset - 1) * limit

        if res['page']['count'] > 0:
            res['list'] = db.session.query(Gzp).filter(*filters)
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

    def getGzpListByUser(self, user, filters, order, field=(), page=0, per_page=15):
        """
            列表
            :param field: tuple 字段
            :param user: obj  查询用户条件
            :param page: int 页数
            :param per_page:
            :param order: obj 排序
            :param filters: set 查询条件
            :param offset: int 偏移量
            :param limit: int 取多少条
            :returns: dict
        """
        res = {}
        res['page'] = {}
        res['page']['count'] = user.gzps.filter(*filters).count()
        res['list'] = []
        res['page']['total_page'] = self.get_page_number(res['page']['count'], per_page)
        res['page']['current_page'] = page
        if page != 0:
            offset = (page - 1) * per_page

        if res['page']['count'] > 0:
            res['list'] = db.session.query(Gzp).filter(*filters)
            res['list'] = res['list'].order_by(order).offset(offset).limit(per_page).all()
        if not field:
            res['list'] = [c.to_dict() for c in res['list']]
        else:
            res['list'] = [c.to_dict(only=field) for c in res['list']]
        return res
