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
from app.Models.Model import member_gzp, wt_gzp
from app import db
from app.Vendor.Decorator import classTransaction


class Gzp(db.Model, BaseModel, SerializerMixin):
    __tablename__ = 'gzps'

    id = db.Column(db.Integer, primary_key=True)
    # 定义维护单与工作票 一对多关系 外键
    wtms = db.relationship("WTMaintain", backref="gzp", lazy='dynamic', cascade='all, delete-orphan',
                           passive_deletes=True)
    gzp_id = db.Column(db.String(50), unique=True)  # 工作票票号
    firm = db.Column(db.String(100))  # 单位
    pstart_time = db.Column(db.DateTime)  # 计划开始时间
    pstop_time = db.Column(db.DateTime)  # 计划结束时间
    error_code = db.Column(db.String(100))  # 故障代码
    error_content = db.Column(db.String(100))  # 故障内容
    task = db.Column(db.String(500))  # 任务
    postion = db.Column(db.String(100), server_default='整机')  # 工作位置
    sign_time = db.Column(db.DateTime)  # 签发时间
    allow1_time = db.Column(db.DateTime)  # 值班许可时间
    end1_time = db.Column(db.DateTime)  # 值班许可终结时间
    allow2_time = db.Column(db.DateTime)  # 现场许可时间
    end2_time = db.Column(db.DateTime)  # 现场许可终结时间
    is_end = db.Column(db.Boolean, default=False)  # 是否终结

    sign_person_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # 签发的工作票 外键
    sign_person = db.relationship('User', foreign_keys=[sign_person_id])  # 签发的工作票

    manage_person_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # 担任工作负责人的工作票 外键
    manage_person = db.relationship('User', foreign_keys=[manage_person_id])  # 担任负责人的工作票

    allow1_person_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # 值班许可的工作票
    allow1_person = db.relationship('User', foreign_keys=[allow1_person_id])

    allow2_person_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # 现场许可的工作票
    allow2_person = db.relationship('User', foreign_keys=[allow2_person_id])  # 现场许可的工作票

    members = db.relationship("User", secondary=member_gzp, backref=db.backref('gzps', lazy='dynamic'),
                              lazy="dynamic")  # 工作班成员
    wts = db.relationship("WT", secondary=wt_gzp, backref=db.backref('gzps', lazy='dynamic'),
                          lazy="dynamic")  # 风机号


    def to_dict(self, only=()):
        resp_dict = {
            'id': self.id,
            'wtms': [{'id': x.id, 'wt_id': x.wt_id, 'stop_time': x.stop_time, 'start_time': x.start_time,
                      'lost_power': x.lost_power, 'time': x.time} for x in self.wtms],
            'gzp_id': self.gzp_id,
            'firm': self.firm,
            'pstart_time': self.pstart_time,
            'pstop_time': self.pstop_time,
            'error_code': self.error_code,
            'error_content': self.error_content,
            'task': self.task,
            'postion': self.postion,
            'sign_time': self.sign_time,
            'allow1_time': self.allow1_time,
            'end1_time': self.end1_time,
            'allow2_time': self.allow2_time,
            'end2_time': self.end2_time,
            'is_end': self.is_end,
            'sign_person_id': self.sign_person_id,
            'manage_person_id': self.manage_person_id,
            'allow1_person_id': self.allow1_person_id,
            'allow2_person_id': self.allow2_person_id,
            'members': [{'id': x.id, 'name': x.name} for x in self.members],
            'wts': [x.id for x in self.wts]
        }
        if only:
            resp_dict = {k: v for k, v in resp_dict.items() if k in only}
        return resp_dict

    def getGzpList(self, page, per_page):
        data = self.getList({}, Gzp.pstart_time.desc(), (), page, per_page)
        return data

    def getGzpModelList(self, page, per_page):
        return self.getModelList({}, Gzp.pstart_time.desc(), page, per_page)

    def getFirmList(self, filters):
        res = db.session.query(Gzp.firm).filter(*filters).distinct().all()
        return [x[0] for x in res]

    def getList(self, filters, order, field=(), offset=0, limit=15):
        """
            列表
            @param set filters 查询条件
            @param obj order 排序
            @param tuple field 字段
            @param int offset 偏移量
            @param int limit 取多少条
            @return dict
        """
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

    def getModelList(self, filters, order, offset=0, limit=15):
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

    # 获取工作票信息
    @staticmethod
    def get(gzp_id):
        return db.session.query(Gzp).filter_by(gzp_id=gzp_id).first()

    # 增加工作票
    @classTransaction
    def add(self, gzp):
        db.session.add(gzp)
        return True

    # 更新工作票
    def update(self):
        return db.session.commit()

    # 根据id删除工作票
    def delete(self, gzp_id):
        self.query.filter_by(gzp_id=gzp_id).delete()
        return db.session.commit()
