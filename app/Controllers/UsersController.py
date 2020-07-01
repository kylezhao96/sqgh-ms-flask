'''
@Author: hua
@Date: 2018-08-30 10:52:23
@LastEditors  : hua
@LastEditTime : 2019-12-18 14:13:46
'''
from app import app
from app.Controllers.BaseController import BaseController
from app.Vendor.Utils import Utils
from app.Models import User
from app.Service.TableService import TableService
from app.Models.Log import Log
from app.Vendor.UsersAuthJWT import UsersAuthJWT
from app.Vendor.Decorator import validator
from flask import request
from app.env import Permissions


@app.route('/', methods=['GET'])
def index():
    """ 测试 """
    Log().add({
        "type": 1,
        "level": 1,
        "data": "1"
    })
    return BaseController().successData(msg='启动成功')


@app.route('/api/users', methods=['GET'])
def get_users():
    res = []
    companys1 = User().getAll(User, {User.company == '石桥子风电场'})
    companys2 = User().getAll(User, {User.company != '石桥子风电场'})
    if companys1:
        res.append({
            'label': '石桥子风电场',
            'data': companys1
        })
    if companys2:
        res.append({
            'label': '其他',
            'data': companys2
        })
    return BaseController().successData(result=res, msg='读取成功')


@app.route('/api/user', methods=['POST'])
def addUser():
    name = request.json.get('name')
    oa_account = request.json.get('oa_account')
    company = request.json.get('company')
    new_user = User()
    new_user.name = name
    new_user.oa_account = oa_account
    new_user.company = company
    new_user.status = 0
    User().add(new_user)
    return BaseController().successData(msg='用户增加成功')


@app.route('/user/info', methods=['POST'])
def getInfo():
    token = request.json.get('token')
    if not token:
        return BaseController().error(msg='token为空')
    filters = {User.remember_token == token}
    field = ('id', 'name', 'oa_account', 'status', 'company', 'created_at', 'updated_at', 'role_id', 'role_creator_id',
             'role_create_time', 'role_status')
    user_info = User().getOne(filters=filters, field=field)
    if not user_info:
        return BaseController().error(msg='查询失败')
    print(user_info)
    user_info['role'] = {
        'id': user_info['role_id'],
        'status': user_info['role_status'],
        'creatorId': user_info['role_creator_id'],
        'createTime': user_info['role_create_time'],
        'permissions': Permissions[user_info['role_id']]
    }
    del user_info['role_creator_id'], user_info['role_create_time'], user_info['role_status']
    return BaseController().successData(result=user_info, msg='获取成功')
