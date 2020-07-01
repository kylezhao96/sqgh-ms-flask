'''
@Author: hua
@Date: 2019-07-23 15:36:31
@description: 
@LastEditors  : hua
@LastEditTime : 2019-12-18 14:17:28
'''
from app.Models.Model import HtLog
from app import db
import time

class LogService:
    """ 
        日志服务层 
    """
    def add(self, data, type=1, level=1):
        """ 
        添加
        @param: string  data
        @param: integer type
        @param: integer level
        @retrun integer boolean
        """
        data = {
            'data': data,
            'type': type,
            'level': level,
            'create_time': int(time.time())
        }
        try:
            log = HtLog(**data)
            db.session.add(log)
            db.session.flush()
            id = log.id
            db.session.commit()
            return id
        except  Exception as e:
            db.session.rollback()  
            return 0
    
        
        