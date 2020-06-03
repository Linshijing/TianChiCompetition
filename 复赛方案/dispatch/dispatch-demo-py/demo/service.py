from .dto import DispatchRequest, DispatchSolution, ActionNode, CourierPlan
from .context import DispatchContext
from typing import Dict, List
#from .solver import BaseSolver
import pandas as pd
import numpy as np
import math
from sklearn.externals import joblib
import time 




class DispatchService:
    def __init__(self):

        column_pro = ['概率0','概率1','概率2','概率3','概率4','概率5','概率6','概率7','概率8','概率9','概率10','概率11']
        column_lat =['zonelat0','zonelat1','zonelat2','zonelat3','zonelat4','zonelat5','zonelat6','zonelat7','zonelat8','zonelat9','zonelat10','zonelat11']
        column_lon = ['zonelon0','zonelon1','zonelon2','zonelon3','zonelon4','zonelon5','zonelon6','zonelon7','zonelon8','zonelon9','zonelon10','zonelon11']
        data_path = './demo/model/'
        IDlist = ['680507','725011','730221','738333','738432','1048660']
        #IDlist=['725011']
        dictData = {}  # 
        for ID in IDlist:
            data = pd.read_csv(data_path+ID+'a.txt')
            dictData.update({ID:data})


        self.data={}
        for ID in IDlist: # 对每个商圈进行整理
            data =dictData.get(ID)
            timeN = len(data)  # 时间段个数
            timearry = data['时间'].values # 时间区间值
            txt = open(data_path+ID+'b.txt') # 对应商圈
        
            alltxt = txt.readlines()
            s=int((len(data.columns)-5)/3) # 商家聚类中心数
            dict_shangquan={}
            for i in range(timeN):
                dict_time1 ={}
                pro=[]
                zonelat=[]
                zonelon=[]
                for j in range(s):
                    pro.append(data.loc[i,column_pro[j]])
                    zonelat.append(data.loc[i,column_lat[j]])
                    zonelon.append(data.loc[i,column_lon[j]])
                dict_time1.update({'概率':pro,'商家lat':zonelat,'商家lon':zonelon})
                dict_time1.update({'订单量':data.loc[i,'订单数']})
                dict_time1.update({'中心lat':data.loc[i,'中心lat']})
                dict_time1.update({'中心lon':data.loc[i,'中心lon']})
                dict_time1.update({'用户':data.loc[i,'用户']})
                txttime = alltxt[i].rstrip("\n")
                txttime1 = txttime.split('#')
                shop_class =[int(c) for c in txttime1]
                
                dict_time1.update({'骑手额定容量':shop_class})

                dict_shangquan.update({str(i):dict_time1})
            txt.close()
            model = joblib.load(data_path+ID+'.pkl')
            model_usr = []
            for m in range(s):
                model_usr.append(joblib.load(data_path+ID+str(m)+'.pkl'))
            dict_shangquan.update({'model':model})
            dict_shangquan.update({'时间':timearry})
            dict_shangquan.update({'用户模型':model_usr})
            self.data.update({ID:dict_shangquan})


        self.serviceContext: Dict[str, DispatchContext] = {}

    def dispatch(self, request: DispatchRequest):
        #start= time.time()
        areaId = request.areaId
        if request.isFirstRound:
            context = DispatchContext(areaId, request.requestTimestamp,self.data.get(areaId))
            self.serviceContext[areaId] = context
        else:
            context = self.serviceContext.get(areaId)
            if context is None:
                emptySolution = DispatchSolution([])
                return emptySolution
            else:
                if request.isLastRound:
                    context.setIsEndOfTest(True)
            context.refresh(request.requestTimestamp)

        #context.timeRecord.append(request.requestTimestamp)
        context.addOnlineCouriers(request.couriers)
        context.addDispatchingOrders(request.orders)
        if context.Yes or context.isEndOfTest:
            context.assignForShop()
            context.assignForOrder()
            courierPlans=context.getResult()
            context.Yes =False
        else:
            courierPlans=[]
        #context.caculation()
        #solver = self.getSolver(context)
        #courierPlans = solver.solve()
        #for cp in courierPlans:
            #for a in cp.planRoutes:
                #a.setSubmitted(True)
        #assignedIds = solver.getAssignedOrderIds()
        #context.markAllocatedOrders(assignedIds)
        #while len(context.orderPool.getDispatchingOrders()) != 0 and context.isEndOfTest:
            #aheadTime = 10 * 60
            #context.setTimeStamp(context.timeStamp + aheadTime)
            #context.timeRecord.append(context.timeStamp + aheadTime)
            #lastRoundSolver = self.getSolver(context)
            #tmpPlans = lastRoundSolver.solve()
            #for cp in tmpPlans:
                #for a in cp.planRoutes:
                    #a.setSubmitted(True)
            #context.markAllocatedOrders(lastRoundSolver.getAssignedOrderIds())
        #if context.setIsEndOfTest:
            #df = pd.DataFrame({'时间':context.timeRecord,'新增订单':context.orderNew,'未完成订单':context.unfinish,'新增骑手数量':context.riderNew,'空闲骑手数量':context.riderFree,'骑手容量':context.RongLiang,'骑手总容量':context.allRongliang})
            #ser = pd.Series(context.orderRecord)
            #df.to_csv('./data'+str(context.areaId)+'.txt',index=False)
            #ser.to_csv('./order'+str(context.areaId)+'.txt')


        solution = DispatchSolution(courierPlans)
        #if request.isLastRound:
            #end = time.time()
            #print(end-start)
        return solution

    #def getSolver(self, context: DispatchContext) -> BaseSolver:
        #return BaseSolver(context)



