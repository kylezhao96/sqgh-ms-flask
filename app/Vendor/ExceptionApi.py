'''
@Author: hua
@Date: 2019-05-30 10:41:29
@LastEditors  : hua
@LastEditTime : 2019-12-18 15:05:31
'''
from flask import jsonify, make_response
from app.env import DEBUG_LOG, SAVE_LOG
from app.Vendor.Log import log
from app.Vendor.Utils import Utils
from app.Service.LogService import LogService
import traceback,sys
from app import db

def ExceptionApi(code, e):
    """ 接口异常处理 """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if DEBUG_LOG:
        if SAVE_LOG == 1:
            log().exception(e)
        elif SAVE_LOG == 2:
            LogService().add(e, 1, 3) #导致文件互相引用
    body = {}
    body['error_code'] = code
    body['error'] = True
    body['show'] = False
    body['debug_id'] = Utils.unique_id()
    db.session.close()
    #这里exc_type 和exc_value信息重复，所以不打印
    body['traceback'] = traceback.format_exception(exc_type, exc_value, exc_traceback)
    return make_response(jsonify(body))