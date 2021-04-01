""" author:hua
    date:2018.5.9
    工具类，封装一些通用方法
"""
from app.env import ALLOWED_EXTENSIONS
from app.Vendor.Code import Code
import time
from decimal import Decimal, ROUND_HALF_UP

validation = {
    # 验证规则
    'required': {
        True: '必须',
        False: '非必须'
    },
    'type': '类型',
    'string': '字符串',
    'integer': '整形',
    'minlength': '最小长度',
    'maxlength': '最大长度',
    # 验证字段
    'nickName': '昵称',
    'headImg': '头像',
    'email': '邮箱',
    'password': '密码'
}


class Utils:
    """
    * 用于sql结果列表对象类型转字典
    * @param list data
    * @return dict
    """

    @staticmethod
    def db_l_to_d(data):
        data_list = []
        for val in data:
            val_dict = val.to_dict()
            data_list.append(val_dict)
        data = {}
        data = data_list
        return data

    ''' 
    * 用于sql结果对象类型转字典
    * @param object obj
    * @return dict
    '''

    @staticmethod
    def class_to_dict(obj):
        """把对象(支持单个对象、list、set)转换成字典"""
        is_list = obj.__class__ == [].__class__
        is_set = obj.__class__ == set().__class__
        if is_list or is_set:
            obj_arr = []
            for o in obj:
                # 把Object对象转换成Dict对象
                dict = {}
                dict.update(o.__dict__)
                obj_arr.append(dict)
                return obj_arr
        else:
            dict = {}
            dict.update(obj.__dict__)
            return dict

    """ 验证文件类型
        @param string filename
        return string path
    """

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    """ uuid,唯一id 
        return string id
    """

    @staticmethod
    def unique_id(prefix=''):
        return prefix + hex(int(time.time()))[2:10] + hex(int(time.time() * 1000000) % 0x100000)[2:7]

    """ 
    * 格式化验证错误描述
    * @param string name
    * @param dict rules
    * @param dict msg
    * @return string
    """

    @staticmethod
    def validateMsgFormat(name, rules, msg):
        # 根据规则生成返回
        if not msg:
            msgFormat = dict()
            for key in rules:
                if key == 'required':
                    ruleMsg = ''
                    actionMsg = validation[key][rules[key]]
                elif key == 'maxlength':
                    ruleMsg = validation[key]
                    actionMsg = rules[key]
                elif key == 'minlength':
                    ruleMsg = validation[key]
                    actionMsg = rules[key]
                else:
                    ruleMsg = validation[key]
                    actionMsg = validation[rules[key]]
                msgFormat[key] = "{} {} {}".format(validation[name], ruleMsg, actionMsg)
            return msgFormat
        return msg

    """ 
    * 自定保留两位小数函数，防止错误进位情况
    * @param float d
    * @param int n
    * @return Decimal
    """

    @staticmethod
    def realRound(d, n=0):
        format = '0.'
        while (n):
            format = format + '0'
            n = n - 1
        return Decimal(str(d)).quantize(Decimal(format), rounding=ROUND_HALF_UP)
