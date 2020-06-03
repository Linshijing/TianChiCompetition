from typing import Dict, List
import math
class Location(object):
    def __init__(self, _latitude, _longitude):
        self.latitude = _latitude
        self.longitude = _longitude

    def keys(self):
        return ['latitude', 'longitude']

    def __getitem__(self, item):
        return getattr(self, item)


class Courier(object):
    def __init__(self, _id, _areaId, _loc, _speed, _maxLoads, _status):
        self.id = _id
        #self.areaId = _areaId
        self.loc = _loc # 最后一个动作完成时的位置
        self.speed = _speed
        self.maxLoads = _maxLoads
        self.status = _status  # 0： 空闲，1 取单路，2：送单
        self.time =0 # 最后一个动作完成时间
        self.shopOrder=0 # 骑手到店的order
        self.dis = 0 # 骑手到商家中心的距离
        self.rongliangSheng =_maxLoads # 剩余容量
        self.planRoutes: List[ActionNode] = [] #
        self.orders: List[Order] = []
        self.orderNumber =0
        self.NoPickOrders=[]

    def keys(self):
        return ['id', 'areaId', 'loc', 'speed', 'maxLoads']

    def __getitem__(self, item):
        return getattr(self, item)

    #def setLoc(self, loc):
        #self.loc = loc

    #def setsetPlanRoutes(self, _planRoutes):
        #self.planRoutes = _planRoutes


class Order(object):
    def __init__(self, _areaId, _id, _srcLoc, _dstLoc, _status, _createTimestamp, _promiseDeliverTime,
                 _estimatedPrepareCompletedTime):
        #self.areaId = _areaId
        self.id = _id
        self.srcLoc = _srcLoc
        self.dstLoc = _dstLoc
        #self.status = _status
        self.createTimestamp = _createTimestamp
        self.promiseDeliverTime = _promiseDeliverTime
        self.estimatedPrepareCompletedTime = _estimatedPrepareCompletedTime
        self.shop=0
        self.user=0
        self.dis =0 # 订单距离骑手

    def keys(self):
        return ['id', 'areaId', 'srcLoc', 'dstLoc', 'status',
                'createTimestamp', 'promiseDeliverTime', 'estimatedPrepareCompletedTime']

    def __getitem__(self, item):
        return getattr(self, item)

    # def setStatus(self, status):
        #self.status = status


class ActionNode(object):
    def __init__(self, _actionType, _orderId, _actionTimestamp): #_isSubmitted, _needSubmitTime):
        self.actionTime = _actionTimestamp
        self.actionType = _actionType
        self.orderId = _orderId
        #if _isSubmitted is None:
            #self.isSubmitted = False
        #else:
            #self.isSubmitted = _isSubmitted
        #if _needSubmitTime is None:
            #self.needSubmitTime = -1
        #else:
            #self.needSubmitTime = _needSubmitTime

    def keys(self):
        return ['actionType', 'orderId', 'actionTimestamp']

    def __getitem__(self, item):
        return getattr(self, item)

    #def setSubmitted(self, _isSubmitted):
        #self.isSubmitted = _isSubmitted




class CourierPlan(object):
    def __init__(self, _courierId, _planRoutes):
        self.courierId = _courierId
        self.planRoutes: List[ActionNode] = _planRoutes

    def keys(self):
        return ['courierId', 'planRoutes']

    def __getitem__(self, item):
        return getattr(self, item)


class DispatchRequest(object):
    def __init__(self, _requestTimestamp, _areaId, _isFirstRound, _isLastRound, _couriers, _orders):
        self.requestTimestamp = _requestTimestamp
        self.areaId = _areaId
        self.isFirstRound = _isFirstRound
        self.isLastRound = _isLastRound
        self.couriers = _couriers
        self.orders = _orders

    def keys(self):
        return ['requestTimestamp', 'areaId', 'isFirstRound', 'isLastRound',
                'couriers', 'orders']

    def __getitem__(self, item):
        return getattr(self, item)

class Shop(object):
    def __init__(self,pro,ordersAll,zhongxin,use,usrN,usrModel):
        self.pro = pro # 该商家中心订单产生概率
        self.maxRong = int(ordersAll*pro)
        self.zhongxin = zhongxin

        self.freeRider = [] # 一个订单都没有的骑手
        self.orders =[] # 待分配的订单
        self.minRong =0 # 最小容量
        self.rongliang =0 # 已有容量
        self.usrRider =[] # 每个用户的骑手
        self.user = use # 每个用户的额定骑手容量
        #self.usrRan = math.pi/usrRan # 用户中心分配的角度 
        self.rongliangAll =0 # 商家中心当前的总容量
        self.userModel = usrModel

        # 存放每个用户中心对应的骑手
        for i in range(usrN):
            self.usrRider.append([])
    def reflash(self,pro,ordersAll,use):
        self.pro = pro
        self.maxRong = int(ordersAll*pro)
        self.user =use
        




class DispatchSolution(object):
    def __init__(self, _courierPlans):
        self.courierPlans = _courierPlans

    def keys(self):
        return ['courierPlans']

    def __getitem__(self, item):
        return getattr(self, item)


class Response(object):
    def __init__(self, _code, _result, _message):
        self.code = _code
        self.result = _result
        self.message = _message

    def keys(self):
        return ['code', 'result', 'message']

    def __getitem__(self, item):
        return getattr(self, item)
