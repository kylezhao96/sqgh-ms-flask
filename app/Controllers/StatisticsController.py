from app import app
from app.Controllers.BaseController import BaseController
from app.Models import Statistics


@app.route('/api/statistics/uncompleted', methods=['GET'])
def get_uncompleted_statistics():
    statisticsList = Statistics().getList({Statistics.completed is not True})
    return BaseController().successData(result=statisticsList)
