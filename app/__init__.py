'''
@Author: hua
@Date: 2018-08-30 10:52:23
@LastEditors  : hua
@LastEditTime : 2019-12-18 14:52:28
'''
from flask import Flask, Blueprint
# 权限模块 https://github.com/raddevon/flask-permissions
# from flask_permissions.core import Permissions
from apscheduler.schedulers.blocking import BlockingScheduler
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from app.Vendor.Code import Code
import environment as e
from app.env import Config
# 读取启动环境
environment = e.read()

# 普通json带error_code风格使用此app示例
app = Flask(__name__)
CORS(app, supports_credentials=True)
# 注册权限
# perms = Permissions(app, db, None)
# 实例化websocket
async_mode = 'gevent'
socketio = SocketIO(app, async_mode=async_mode)
# 配置 sqlalchemy  数据库驱动://数据库用户名:密码@主机地址:端口/数据库?编码
db = SQLAlchemy()
migrate = Migrate()
app.config.from_object(Config)
db.init_app(app)
migrate.init_app(app, db)
api = Blueprint('api', __name__)
from app.Vendor.ExceptionApi import ExceptionApi


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


# 挂载500异常处理,并记录日志
# if environment == 'run' or environment == 'restful':
@app.errorhandler(Exception)
def error_handler(e):
    return ExceptionApi(Code.ERROR, e)


if environment == 'socket':
    @socketio.on_error_default  # Handles the default namespace
    def error_handler(e):
        return ExceptionApi(Code.ERROR, e)
# 引入使用的控制器
if environment == 'run' or environment == 'restful':
    from app.Controllers import UsersController, RestfulController, AdminController, CdfController, AuthController, \
        GzpController, StatisticsController, ImpController
    # 蓝图，新增的后台部分代码
    from app.Controllers.AdminController import admin
    from app.Controllers.AuthController import auth
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(api, url_prefix='/api')

if environment == 'socket':
    # 引入socketio控制层
    from app.Controllers import SocketController
# 引入数据库事件
from app.Event import Log

# 在socket模式下请用后台线程作为计划任务
if environment == 'job':
    # 任务调剂
    sched = BlockingScheduler()
    # 引入任务
    from app.Job import Cron, Interval
