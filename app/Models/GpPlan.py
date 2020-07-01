import calendar

from sqlalchemy_serializer import SerializerMixin

from app.Models.BaseModel import BaseModel
from app.Models.Model import HtGpPlan


class GpPlan(HtGpPlan, BaseModel, SerializerMixin):
    @staticmethod
    def getGpPlan(year, month=0, day=0, num=0):
        res = 0
        filters = {
            GpPlan.year == year
        }
        if month != 0:
            filters.add(GpPlan.month == month)
        if num != 0:
            filters.add(GpPlan.num == num)
        gp_plan_lists = GpPlan().getAll(GpPlan, filters)
        for gp_plan in gp_plan_lists:
            res = res + gp_plan['plan_gp']
            if day != 0:
                res = res * day / calendar.monthrange(year, month)[1]
        return res

    @staticmethod
    def getGpPlanUntil(year, month, day=0, num=0):
        if day:
            return GpPlan.getGpPlan(year, month, day, num) + GpPlan.getGpPlanUntil(year, month-1)
        if month:
            return GpPlan.getGpPlan(year, month) + + GpPlan.getGpPlanUntil(year, month-1)
        return 0
