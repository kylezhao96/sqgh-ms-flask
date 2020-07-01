'''
@Author: hua
@Date: 2019-12-18 14:37:29
@description: 
@LastEditors  : hua
@LastEditTime : 2019-12-18 14:40:20
'''
from app.Vendor.Decorator import classTransaction
from app.Models.User import User
from app import db


class TableService:

    @classTransaction
    def lock(self):
        """ 行级锁 """
        query = db.session.query(User).filter(User.id == 34).with_for_update().first();
        print('SQL : %s' % str(query))
        db.session.execute("select sleep(10)")
