"""
@Author: kyle
@Date: 2020-06-19 20:56
@description:
@LastEditors: kyle
@LastEditTime: 2020-06-19 20:56
"""
import time

from sqlalchemy import desc, asc
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.Models.BaseModel import BaseModel
from app import db
from app.Vendor.Decorator import classTransaction


class User(db.Model, BaseModel, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    oa_account = db.Column(db.String(20), unique=True)
    oa_password = db.Column(db.String(100))
    company = db.Column(db.String(100))
    status = db.Column(db.Integer)
    remember_token = db.Column(db.String(200))
    created_at = db.Column(db.Integer)
    updated_at = db.Column(db.Integer)
    role_id = db.Column(db.String(100))
    role_name = db.Column(db.String(100))
    role_creator_id = db.Column(db.String(100))
    role_create_time = db.Column(db.Integer)
    role_status = db.Column(db.Integer)
    #
    # serialize_rules = ('-password',)
    # 描述suggest表关系，第一个参数是参照类,要引用的表，
    # 第二个参数是backref为类Suggest申明的新方法，backref为定义反向引用，
    # 第三个参数lazy是决定什么时候sqlalchemy从数据库中加载数据
    # 这里缺少外键，暂不展开
    # suggest = db.relationship('Suggest')

    """  def __str__(self):
        return "User(id='%s')" % self.id """
    """
        获取一条
        @param set filters 查询条件
        @param obj order 排序
        @param tuple field 字段
        @return dict
    """

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
            field = ('id', 'name', 'oa_account', 'oa_password', 'company', 'status', 'remember_token', 'created_at',
                     'updated_at',
                     'role_id', 'role_name', 'role_create_time', 'role_status')
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
    def update(id, oa_account=(), oa_password=(), company=(), status=(), created_at=(), role_id=(), updated_at=(),
               role_name=(), role_create_time=(), role_creator_id=(), role_status=(), remember_token=()):
        user = db.session.query(User).filter_by(id=id).first()
        user.oa_account = oa_account if oa_account else user.oa_account
        user.oa_password = User.set_password(oa_password) if oa_password else user.oa_password
        user.company = company if company else user.company,
        user.status = status if status else user.status,
        user.created_at = created_at if created_at else user.created_at,
        user.role_id = role_id if role_id else user.role_id,
        user.role_name = role_name if role_name else user.role_name,
        user.role_create_time = role_create_time if role_create_time else user.role_create_time,
        user.role_creator_id = role_creator_id if role_creator_id else user.role_creator_id,
        user.role_status = role_status if role_status else user.role_status
        user.updated_at = int(time.time()) if updated_at else user.updated_at
        user.remember_token = remember_token if remember_token else user.remember_token
        return db.session.commit()

    # 根据id删除用户
    def delete(self, id):
        self.query.filter_by(id=id).delete()
        return db.session.commit()

    # # 更新更新时间
    # @staticmethod
    # def update(id, updated_at, token):
    #     db.session.query(User).filter_by(id=id).update({'updated_at': updated_at, 'remember_token': token})
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
