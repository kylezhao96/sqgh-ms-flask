"""
@Author: hua
@Date: 2018-08-30 10:52:23
@description:
@LastEditors: hua
@LastEditTime: 2019-11-28 20:05:49
"""

# debug
DEBUG_LOG = True
# log save 1为文件形式，2为数据库形式，默认数据库
SAVE_LOG = 1
# upload
UPLOAD_FOLDER = '/uploads/'  # 允许目录
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 允许大小16MB
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])  # 允许文件

# 相关文件目录
YEAR = '2020'
DESK_PATH = r"C:\Users\admin\Desktop"
OMS_PATH = DESK_PATH + r"\1报表文件夹\日报表\\" + YEAR + r"年\\" + YEAR + r"年OMS日报.xlsx"
TY_PATH = DESK_PATH + r"\1报表文件夹\每日00：30前石桥风电场每日风机电量、风速统计表报送诸城桃园风场公共邮箱\\" + YEAR + \
          r"年\石桥风电场报送每日风机电量风速统计表" + YEAR + r".xlsx"
EXCEL_PATH = DESK_PATH + r"\1报表文件夹\日报表\\" + YEAR + r"年\\" + YEAR + r"年石桥风电场日报表.xlsx"
driverLoc = r"D:\submitTable\driver\IEDriverServer.exe"


# mysql
# SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess'
class Config(object):
    # 最好用环境变量方式设置密钥
    # jwt
    JWT_LEEWAY = 604800
    SECRET_KEY = '7PXsHcHGfa4e3kEs8Rvcv8ymjI0UeauX'
    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess'
    DIALECT = 'mysql'
    DRIVER = 'pymysql'
    USERNAME = 'kylezhao'
    PASSWORD = '123456'
    HOST = '47.93.199.183'
    PORT = '3306'
    DATABASE = 'test'

    SQLALCHEMY_DATABASE_URI = '{}+{}://{}:{}@{}:{}/{}?charset=utf8'.format(
        DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT, DATABASE
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_MAX_OVERFLOW = 5




