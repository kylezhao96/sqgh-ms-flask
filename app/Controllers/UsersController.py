'''
@Author: hua
@Date: 2018-08-30 10:52:23
@LastEditors  : hua
@LastEditTime : 2019-12-18 14:13:46
'''
from app import app, api
from app.Controllers.BaseController import BaseController
from app.Vendor.Utils import Utils
from app.Models import User, Gzp
from app.Service.TableService import TableService
from app.Models.Log import Log
from app.Vendor.UsersAuthJWT import UsersAuthJWT
from app.Vendor.Decorator import validator
from flask import request
# from app.env import Permissions


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
    companys1 = User().getAll(User, {User.company == '石桥子风电场'}, field=('name', 'company'))
    companys2 = User().getAll(User, {User.company != '石桥子风电场' or User.company is None}, field=('name', 'company'))
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


@api.route('/user/info', methods=['GET'])
def getInfo():
    token = request.args.get("token")
    if not token:
        return BaseController().error(msg='token为空')
    filters = {User.remember_token == token}
    field = ('id', 'name', 'oa_account', 'status', 'last_login_time', 'last_login_ip', 'created_time', 'deleted', 'role_id')
    user_info = User().getOne(filters=filters, field=field)
    if not user_info:
        return BaseController().error(msg='查询失败')
    return BaseController().successData(result=user_info, msg='获取成功')


@app.route('/api/users', methods=['POST'])
def search_users():
    data = request.get_json() or ''
    res = set()
    if data:
        res_list = User().getList(User, {User.name.contains(data['value'])}, field=('name',))['list']
        users_name = [x['name'] for x in res_list]
        if len(users_name) == 0:
            res.add(data['value'])
        res.update(users_name)

    else:
        res_list = Gzp().getList({}, order=Gzp.gzp_id.desc(), field=('manage_person_id', 'members'), offset=0, limit=5)[
            'list']
        for item in res_list:
            manager_person_name = User().getOne(filters={User.id == item['manage_person_id']}, field=('name',))['name']
            members_name = [User().getOne(filters={User.id == x['id']}, field=('name',))['name'] for x in
                            item['members']]
            res.add(manager_person_name)
            res.update(members_name)
    return BaseController().successData(result=list(res))
