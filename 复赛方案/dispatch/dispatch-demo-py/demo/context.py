from .dto import Order, Courier, ActionNode,Location,Shop,CourierPlan
from .pool import OrderPool, CourierPool
from typing import Dict, List
from demo.dto import Location,Shop
import math
import itertools
class DispatchContext:
    def __init__(self, areaId, timeStamp,data,isEndOfTest=False):
        self.areaId = areaId  # 商圈ID
        self.timeStamp = timeStamp  # 当前时间
        self.isEndOfTest = isEndOfTest #  是否最后一轮
        self.timeFresh = timeStamp

        self.timeStep =0
        self.data = data # 整个商圈不同时刻的参数信息 
        self.timeQujian=data.get('时间') # 时间区间列表
        data_0 = self.data.get(str(self.timeStep)) # 得到时刻i参数信息
        self.shops =[]  # 商家聚类中心
        self.center = Location(data_0.get('中心lat'),data_0.get('中心lon')) # 商圈中心
        self.model = self.data.get('model')
        usrModel = self.data.get('用户模型')
        usrn = data_0.get('用户')

        pro = data_0.get('概率')
        orders = data_0.get('订单量')
        lat = data_0.get('商家lat')
        lon = data_0.get('商家lon')
        usr = data_0.get('骑手额定容量')

        for i in range(len(pro)):
            sp = Shop(pro[i],orders,Location(lat[i],lon[i]),usr[i],usrn,usrModel[i])
            self.shops.append(sp)

        self.riderNew =[] # 无任务订单的空闲骑手
        self.deliverRider=[] # 处于送单的骑手
        self.orderRiderID=[]
        self.Number=0
        self.Yes =False # 是否进行调度的标志

        self.courierPool = CourierPool()
        

    def setIsEndOfTest(self, isEndOfTest):
        self.isEndOfTest = isEndOfTest

    def addOnlineCouriers(self, courierList):
        self.courierPool.addOnlineCouriers(courierList)
        self.riderNew.extend(courierList) # 新上线的骑手
        
    # 转换极坐标对应的角度
    def Ran(self,loc1,loc2):
        lat = loc1.latitude - loc2.latitude
        lon = loc1.longitude -loc2.longitude
        
        if lat<0:
            if lon>0:
                tan =  -lon/lat
                R = math.atan(tan)
                return (math.pi -R)
            elif lon<0:
                tan =  lon/lat
                R = math.atan(tan)
                return(math.pi +R)
            else:
                return math.pi
        elif lat >0:
            if lon>0:
                tan =  lon/lat
                return math.atan(tan)
            elif lon<0:
                tan =  -lon/lat
                R = math.atan(tan)
                return (2*math.pi -R)
            else:
                return 0
        else:
            if lon>0:
                return math.pi/2
            elif lon<0:
                return 3*math.pi/2
            else:
                return 0

    # 将订单划分到各自的商家中心
    def addDispatchingOrders(self, orders):
        for order in orders:
            inp = [[order.srcLoc.latitude,order.srcLoc.longitude]]
            out = self.model.predict(inp)[0]
            order.shop =out
            shop = self.shops[out]
            usr_input = [[self.Ran(order.dstLoc,shop.zhongxin)]]
            order.user = shop.userModel.predict(usr_input)[0]
            self.shops[out].orders.append(order)
    
    # 更新
    def refresh(self, refreshTime):
        self.timeStamp = refreshTime
        self.timeFresh = refreshTime
        self.orderRiderID=[]
        timeY = refreshTime % 86400
        lenth = len(self.timeQujian)
        timeStamp =0
        # 判断是属于哪个时间段的
        for i in range(lenth):
            if timeY < self.timeQujian[i]:
                timeStamp =i
                break
        # 当时段改变了，更新相应的信息
        if self.timeStep != timeStamp:
            data_0 = self.data.get(str(timeStamp))
            pro = data_0.get('概率')
            orders = data_0.get('订单量')
            
            usr = data_0.get('骑手额定容量')
            #print(usr)
            for i,shop in enumerate(self.shops):
                shop.reflash(pro[i],orders,usr[i])

        riderworking =[]
        # 判断处于送单的骑手是否完成了所有的单子
        for courier in self.deliverRider:
            if courier.time < refreshTime:
                self.riderNew.append(courier)
            else:
                riderworking.append(courier)
        self.deliverRider = riderworking

        if self.Number %2 ==0:
            self.Yes =True
        self.Number +=1

    # 距离
    def greatCircleDistance(self, lng1, lat1, lng2, lat2):
       
        # 地球半径
        RADIUS = 6367000.0
        # 导航距离/路面距离 经验系数
        COEFFICIENT = 1.4
        # 经度差值
        deltaLng = lng2 - lng1
        # 纬度差值
        deltaLat = lat2 - lat1
        # 平均纬度
        b = (lat1 + lat2) / 2.0
        # 东西距离
        x = math.radians(deltaLng) * RADIUS * math.cos(math.radians(b))
        # 南北距离
        y = RADIUS * math.radians(deltaLat)
        # 用平面的矩形对角距离公式计算总距离
        return math.sqrt(x * x + y * y)*COEFFICIENT
    
    # 骑手送单排列组合取最优
    def riderDeliver(self,rider):
        lethorder = len(rider.orders) # 订单个数
        bestChoice =0
        a = list(range(lethorder))
        allChoice = list(itertools.permutations(a,lethorder))
        overTimeless =1000
        for i,a in enumerate(allChoice):
            overTime =0
            timeBegier =max(rider.time,self.timeStamp)
            loc_lng = rider.loc.longitude
            loc_lat = rider.loc.latitude
            for j in a:
                order = rider.orders[j]
                time =  timeBegier + math.ceil(self.greatCircleDistance(loc_lng,loc_lat,order.dstLoc.longitude,order.dstLoc.latitude) /rider.speed)
                if time > order.promiseDeliverTime:
                    overTime +=1
                loc_lng = order.dstLoc.longitude
                loc_lat = order.dstLoc.latitude
                timeBegier = time
            if overTime <overTimeless:
                overTimeless = overTime
                bestChoice = i


        order_order =allChoice[bestChoice]
        timeBegier =max(rider.time,self.timeStamp)
        for j in order_order:

            order = rider.orders[j]
            time = max(rider.time,self.timeStamp)+math.ceil(self.greatCircleDistance(rider.loc.longitude,rider.loc.latitude,order.dstLoc.longitude,order.dstLoc.latitude) /rider.speed)
            rider.planRoutes.append(ActionNode(3,order.id,time))
            rider.time = time
            rider.loc= order.dstLoc

        rider.orders =[]
    # 骑手取单排列组合取最优
    def riderPick(self,rider):
        lethorder = len(rider.NoPickOrders) # 订单个数
        if lethorder <5:
            bestChoice =0
            a = list(range(lethorder))
            allChoice = list(itertools.permutations(a,lethorder))
            overTimeless =10000000000
            for i,a in enumerate(allChoice):
                overTime =0
                timeBegier =max(rider.time,self.timeStamp)
                loc_lng = rider.loc.longitude
                loc_lat = rider.loc.latitude
                for j in a:
                    order = rider.NoPickOrders[j]
                    time =  timeBegier + math.ceil(self.greatCircleDistance(loc_lng,loc_lat,order.srcLoc.longitude,order.srcLoc.latitude) /rider.speed)
                    time = max(time,order.estimatedPrepareCompletedTime)
                    overTime =time
                    loc_lng = order.srcLoc.longitude
                    loc_lat = order.srcLoc.latitude
                    timeBegier = time
                if overTime <overTimeless:
                    overTimeless = overTime
                    bestChoice = i

            order_order =allChoice[bestChoice]
            timeBegier =max(rider.time,self.timeStamp)
            for j in order_order:
                order = rider.NoPickOrders[j]
                time = max(rider.time,self.timeStamp)+math.ceil(self.greatCircleDistance(rider.loc.longitude,rider.loc.latitude,order.srcLoc.longitude,order.srcLoc.latitude) /rider.speed)
                rider.planRoutes.append(ActionNode(1,order.id,time))
                time = max(time,order.estimatedPrepareCompletedTime)
                rider.planRoutes.append(ActionNode(2,order.id,time))
                rider.orders.append(order)
                rider.time = time
                rider.loc= order.srcLoc
        else:
            rider.NoPickOrders.sort(key=lambda x:x.estimatedPrepareCompletedTime)
            for order in rider.NoPickOrders:
                time = max(rider.time,self.timeStamp)+math.ceil(self.greatCircleDistance(rider.loc.longitude,rider.loc.latitude,order.srcLoc.longitude,order.srcLoc.latitude) /rider.speed)
                rider.planRoutes.append(ActionNode(1,order.id,time))
                time = max(time,order.estimatedPrepareCompletedTime)
                rider.planRoutes.append(ActionNode(2,order.id,time))
                rider.orders.append(order)
                rider.time = time
                rider.loc= order.srcLoc

        rider.NoPickOrders =[]

    # 根据商家中心的待分配订单数量进行分配骑手
    def assignOnebyOne(self,shops,shops_all):
        for shop in shops:
            for rider in self.riderNew:
                rider.dis=self.greatCircleDistance(shop.zhongxin.longitude,shop.zhongxin.latitude,rider.loc.longitude,rider.loc.latitude)
            self.riderNew.sort(key=lambda x:x.dis,reverse=True)


            # 只要不满足最小容量要求，就添加骑手
            while (shop.rongliang < shop.minRong) and (shop.rongliangAll<=shop.maxRong):
                r = self.riderNew.pop()
                shop.freeRider.append(r)
                shop.rongliang +=1
                shop.rongliangAll += r.maxLoads
            shop.rongliang =0

        shops.sort(key=lambda x:x.pro,reverse=True)
        self.riderNew.sort(key=lambda x:x.maxLoads)
        i=0
        lenthshops = len(shops)
        # 如果存在还有未分配任务的订单的商家中心，将多余分给他们
        if lenthshops>0:
            while len(self.riderNew) >0:
                r = self.riderNew.pop()
                shops[i].freeRider.append(r)
                shops[i].rongliangAll +=r.maxLoads
                i +=1
                i = i % lenthshops
        # 当前所有的商家中心都不存在未分配订单，则多余骑手分给所有的商家中心
        else:
            shops_all.sort(key=lambda x:x.pro,reverse=True)
            lenthshops = len(shops_all)
            while len(self.riderNew) >0:
                r = self.riderNew.pop()
                shops_all[i].freeRider.append(r)
                shops_all[i].rongliangAll +=r.maxLoads
                i +=1
                i = i % lenthshops

    # 根据商家中心所能获得的骑手容量比例进行分配骑手
    def assignbyRate(self,shops,MinRongssum):
        Flg = False
        shops.sort(key=lambda x:x.minRong,reverse =True) # 容量要求从大到小排序
        riderRongs = sum([x.maxLoads for x in self.riderNew])

        for shop in shops:
            shop.minRong = math.ceil(riderRongs*shop.minRong / MinRongssum)
            
            for rider in self.riderNew:
                rider.dis=self.greatCircleDistance(shop.zhongxin.longitude,shop.zhongxin.latitude,rider.loc.longitude,rider.loc.latitude)
            self.riderNew.sort(key=lambda x:x.dis,reverse=True)

            while shop.rongliang < shop.minRong:
                if not len(self.riderNew):
                    Flg = True
                    break
                else:
                    r = self.riderNew.pop()
                    shop.freeRider.append(r)
                    shop.rongliangAll += r.maxLoads
                    shop.rongliang +=r.maxLoads
            shop.rongliang = 0
            if Flg:
                break

    # 给商家聚类中心分配骑手
    def assignForShop(self):
        # 获取所有最小容量不为0的商家
        shops =[] # 存储当前存在订单的商家中心
        shops_all =[] # 存放所有的商家中心
        MinRongssum =0
        for shop in self.shops:
            shop.minRong = len(shop.orders)-len(shop.freeRider)
            if shop.minRong >0:
                MinRongssum +=shop.minRong
                shops.append(shop)
            
            shops_all.append(shop)

        # 骑手的数量大于等于最小容量和 一一分配
        if MinRongssum <= len(self.riderNew):
            self.assignOnebyOne(shops,shops_all)

        # 骑手的数量小于等于最小容量和，按最小容量比例进行分配
        else:
            self.assignbyRate(shops,MinRongssum)
            
    # 将订单分配给骑手
    def assignOrder(self):
        orderList=[0 for o in range(len(self.shops))]
        # 订单分配
        for ss,shop in enumerate(self.shops):
            
            lenth = len(shop.orders)
            orderNotAssign = []
            shop.orders.sort(key=lambda x:x.estimatedPrepareCompletedTime,reverse=True)
            # 还存未分配订单
            while len(shop.orders)>0:
                order = shop.orders.pop() # 订单
                orderNotAssign.append(order) # 把订单加入
                usr_rider =shop.usrRider[order.user] # 用户骑手列表
                if len(usr_rider) >0: # 用户骑手列表不为空，从中选一个
                    for rider in usr_rider:
                        rider.dis = self.greatCircleDistance(order.srcLoc.longitude,order.srcLoc.latitude,rider.loc.longitude,rider.loc.latitude)
                    usr_rider.sort(key =lambda x:x.dis) # 按距离排序
                    for rider in usr_rider:
                        if rider.rongliangSheng >0: # 还有取单容量                            
                            rider.NoPickOrders.append(order)          
                            rider.orderNumber +=1
                            rider.rongliangSheng -=1
                            shop.rongliangAll -=1
                            orderNotAssign.pop()
                            break
                # 判断尚未分配用户中心的骑手
                elif len(shop.freeRider)>0:
                    for rider in shop.freeRider:
                        rider.dis = self.greatCircleDistance(order.srcLoc.longitude,order.srcLoc.latitude,rider.loc.longitude,rider.loc.latitude)

                    shop.freeRider.sort(key=lambda x:x.dis)
                    for rider in shop.freeRider:
                        if rider.rongliangSheng >0: # 还有取单容量
                            rider.NoPickOrders.append(order)
                            rider.orderNumber +=1
                            rider.rongliangSheng -=1
                            shop.rongliangAll -=1
                            shop.usrRider[order.user].append(rider) # 对应用户区间的订单增加一个
                            shop.freeRider.remove(rider) # 从空闲骑手中中删除
                            orderNotAssign.pop()
                            break  
            shop.orders =orderNotAssign
  
    # 骑手进行到店取单规划
    def pickOrder(self):
        #骑手进行取单操作
        for shop in self.shops:
            usrRider = shop.usrRider
            for r in usrRider:
                for rider in r:
                    self.riderPick(rider)
    # 骑手送单规划
    def deliverOrder(self):
        # 决定骑手是否该送单
        for shop in self.shops:
            usrRider = shop.usrRider
            
            # 遍历每一个用户中心
            for r in range(len(usrRider)):

                riderzone = usrRider[r]
                riderzonenew =[]
                # 遍历每个用户中心的骑手
                for rider in riderzone:
                    if len(rider.orders)>= shop.user or rider.rongliangSheng <1 or rider.time< self.timeStamp: # 大于等于额定容量
                        if len(rider.orders)<=4:
                            self.riderDeliver(rider)
                        else:
                            for order in rider.orders:
                                order.dis = self.greatCircleDistance(rider.loc.longitude,rider.loc.latitude,order.dstLoc.longitude,order.dstLoc.latitude)
                            rider.orders.sort(key=lambda x:x.dis)
                            for order in rider.orders:
                                dis = self.greatCircleDistance(rider.loc.longitude,rider.loc.latitude,order.dstLoc.longitude,order.dstLoc.latitude)
                                time1 = max(rider.time,self.timeStamp)+math.ceil(dis/rider.speed)
                                rider.planRoutes.append(ActionNode(3,order.id,time1))
                                rider.time = time1
                                rider.loc = order.dstLoc
                        shop.rongliangAll -=rider.rongliangSheng
                        rider.rongliangSheng = rider.maxLoads
                        rider.orderNumber =0
                        rider.orders =[]

                        self.deliverRider.append(rider)
                    else:
                        riderzonenew.append(rider)
                shop.usrRider[r] = riderzonenew
   
   
    # 给每个订单分配骑手
    def assignForOrder(self):

        self.assignOrder()

        self.pickOrder()

        self.deliverOrder()

        # 判断是否最后一轮调度
        self.lastRound()
    
     # 最后一轮采用的更新
    

    # 最后一轮调度所进行的时间状态更新
    def refreshLast(self):
        
        riderworking =[]
        # 判断处于送单的骑手是否完成了所有的单子
        for courier in self.deliverRider:
            if courier.time < self.timeFresh:
                self.riderNew.append(courier)
            else:
                riderworking.append(courier)
        self.deliverRider = riderworking

   
    # 最后一轮给每个订单分配骑手
    def assignForOrderLast(self):
        self.assignOrder()

        self.pickOrder()

        #骑手进行取单操作
       
        # 决定骑手是否该送单
        for shop in self.shops:
            usrRider = shop.usrRider
            
            # 遍历每一个用户中心
            for r in range(len(usrRider)):
                riderzone = usrRider[r]
                riderzonenew =[]
                # 遍历每个用户中心的骑手
                for rider in riderzone:
                    if len(rider.orders)>= shop.user or rider.rongliangSheng <1 or rider.time < self.timeFresh or len(shop.orders)<1: # 大于等于额定容量
                        
                        if len(rider.orders)<=3:
                            self.riderDeliver(rider)

                        else:
                            for order in rider.orders:
                                order.dis = self.greatCircleDistance(rider.loc.longitude,rider.loc.latitude,order.dstLoc.longitude,order.dstLoc.latitude)
                            rider.orders.sort(key=lambda x:x.dis)
                            for order in rider.orders:
                                dis = self.greatCircleDistance(rider.loc.longitude,rider.loc.latitude,order.dstLoc.longitude,order.dstLoc.latitude)
                                time1 = max(rider.time,self.timeStamp)+math.ceil(dis/rider.speed)
                                rider.planRoutes.append(ActionNode(3,order.id,time1))
                                rider.time = time1
                                rider.loc = order.dstLoc
                        shop.rongliangAll -=rider.rongliangSheng
                        rider.rongliangSheng = rider.maxLoads
                        rider.orders =[]
                        rider.orderNumber =0

                        self.deliverRider.append(rider)
                    else:
                        riderzonenew.append(rider)
                shop.usrRider[r] = riderzonenew


     # 最后一轮调度
    # 最后一轮调度
    def lastRound(self):
        # 是否是最后一轮调度
        if self.isEndOfTest:
            # 还有剩余订单未分配
            while True:
                flase = True
                for shop in self.shops:
                    if len(shop.orders)>0:
                        flase =False
                        break
                if flase:
                    break
                else:
                    self.timeFresh = self.timeFresh+5*60
                    self.refreshLast()
                    self.assignForShop()
                    self.assignForOrderLast()

     # 获取返回结果
    
    # 返回最终结果
    def getResult(self):
        result =[]
        result_1 =[]
        for courier in self.courierPool.couriers:
            if len(courier.planRoutes)>0:
                if courier.id in self.orderRiderID:
                    result_1.append(CourierPlan(courier.id,courier.planRoutes))
                else:

                    result.append(CourierPlan(courier.id,courier.planRoutes))
                courier.planRoutes=[]
        result.extend(result_1)
        return result


