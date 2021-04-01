"""
@Author: kyle
@Date: 2020-06-19 20:56
@description:
@LastEditors: kyle
@LastEditTime: 2020-06-19 20:56
"""
import time

from sqlalchemy import desc, asc, func, inspect
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.Models import Gzp
from app.Models.BaseModel import BaseModel
from app import db
from app.Vendor.Decorator import classTransaction


class User(db.Model, BaseModel, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    oa_account = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(100))
    company = db.Column(db.String(100))
    status = db.Column(db.Integer)
    # telephone = db.Column(db.String(100))
    remember_token = db.Column(db.String(200))
    created_time = db.Column(db.Integer)
    last_login_ip = db.Column(db.String(100))
    last_login_time = db.Column(db.Integer)
    role_id = db.Column(db.String(100))
    deleted = db.Column(db.Integer)

    def getOne(self, filters, order='id desc', field=()):
        res = db.session.query(User).filter(*filters)
        order = order.split(' ')
        if order[1] == 'desc':
            res = res.order_by(desc(order[0])).first()
        else:
            res = res.order_by(asc(order[0])).first()
        if res == None:
            return None
        if not field:
            field = inspect(User).c.keys()
            res = res.to_dict(only=field)
        else:
            res = res.to_dict(only=field)
        return res

    # 设置密码
    @staticmethod
    def set_password(password):
        return generate_password_hash(password)

    # 校验密码
    @staticmethod
    def check_password(hash_password, password):
        return check_password_hash(hash_password, password)

    # 获取用户信息
    @staticmethod
    def get(id):
        return db.session.query(User).filter_by(id=id).first()

    # 增加用户
    @classTransaction
    def add(self, user):
        db.session.add(user)
        return True

    # 修改用户
    @staticmethod
    def update(id, oa_account=(), password=(), status=(), created_time=(), role_id=(), last_login_time=(),
               remember_token=(), last_login_ip=(), deleted=(), name=()):
        user = db.session.query(User).filter_by(id=id).first()
        user.oa_account = oa_account if oa_account else user.oa_account
        user.password = User.set_password(password) if password else user.password
        user.name = name if name else user.name
        user.status = status if status else user.status,
        user.deleted = deleted if deleted else user.deleted,
        user.created_time = created_time if created_time else user.created_time,
        user.role_id = role_id if role_id else user.role_id,
        user.last_login_time = int(time.time()) if last_login_time else user.last_login_time
        user.last_login_ip = last_login_ip if last_login_ip else user.last_login_ip
        user.remember_token = remember_token if remember_token else user.remember_token
        return db.session.commit()

    # 根据id删除用户
    def delete(self, id):
        self.query.filter_by(id=id).delete()
        return db.session.commit()

    # # 更新更新时间
    # @staticmethod
    # def update(id, last_login_time, token):
    #     db.session.query(User).filter_by(id=id).update({'last_login_time': last_login_time, 'remember_token': token})
    #     return db.session.commit()

    # 根据姓名获取用户
    def getByName(self, name):
        if not User.query.filter_by(name=name).first():
            manager = User()
            manager.name = name
            User().add(manager)
            return manager
        else:
            return User.query.filter_by(name=name).first()
