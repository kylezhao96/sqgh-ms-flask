'''
@Author: hua
@Date: 2019-12-18 17:22:18
@description: 
@LastEditors  : hua
@LastEditTime : 2019-12-18 17:23:51
'''
import environment
environment.init("job")
from app import sched
#开始任务
sched.start()