import time

from flask import Blueprint, request
from app.Controllers.BaseController import BaseController
from app.Models import User
from app.Vendor.Decorator import validator
from app.Vendor.UsersAuthJWT import UsersAuthJWT

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['POST'])
def login():
    oa_account = request.json.get('account')
    password = request.json.get('password')
    if not oa_account or not password:
        return BaseController().error('账号和密码不能为空')
    else:
        result = UsersAuthJWT.authenticate(oa_account, password)
        return result


@auth.route('/logout', methods=['POST'])
def logout():
    token = request.json.get('token')
    updated_at = int(time.time())
    if not token:
        return BaseController().error(msg='token为空')
    user = User().getOne(filters={User.remember_token == token})
    if not user:
        return BaseController().error(msg='查询失败')
    User.update(user['id'], remember_token='')
    return BaseController().successData(msg='登出成功')


@auth.route('/register', methods=['POST'])
def register():
    """ 注册 """
    oa_account = request.json.get('account')
    password = request.json.get('password')
    name = request.json.get('name')
    filters = {
        User.oa_account == oa_account
    }
    user_data = User().getOne(filters)
    if user_data is None:
        create_time = int(time.time())
        user = User(
            oa_account=oa_account,
            password=User.set_password(password),
            name=name,
            status=1,
            created_time=create_time,
            role_id='auditor',
        )
        status = user.add(user)
        if status:
            return BaseController().successData(result={'name': name}, msg='注册成功')
        return BaseController().error('注册失败')
    # else:
    #     user = User.get(user_data['id'])
    #     create_time = int(time.time())
    #     User().update(user, oa_account, User.set_password(oa_password), company, 1, create_time, 'admin', '管理员',
    #                   create_time, 'default', 1)
    return BaseController().error('账号已注册')


