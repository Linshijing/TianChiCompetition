import numpy as np
import pandas as pd
import os
import copy
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestClassifier

from sklearn.externals import joblib

# 规范浮点数的小数位,用于经度纬度
def XiaoShu(x):
    return round(x,6)


# 根据模型进行决策决策
def DesicisonModel(trainData):
    dis = 1200 # 距离差大于1200时，直接根据距离大小进行行为决策
    # 构建模型的输入特征
    trainData['距离差'] = trainData['商家距离'] - trainData['客户距离']
    trainData['理论时间差'] = trainData['理论取单时间'] -trainData['理论送单时间']
    trainData['承诺时间差'] = trainData['取单承诺送达时间'] - trainData['送单承诺送达时间']
    trainData['可取理论时间差'] = trainData['取单可取时间'] - trainData['理论取单时间']
    trainData['可取单数'] = trainData['最大负荷量'] - trainData['当前已取单数']
  
    # 加载训练好的模型
    basePath = '../user_data/model_data/decision_model/'
    modelRF1 = joblib.load(basePath+'RFdecision_dis1.pkl')
    modelRF2 = joblib.load(basePath+'RFdecision_dis2.pkl')
    modelRF3 = joblib.load(basePath+'RFdecision_dis3.pkl')
    modelRF4 = joblib.load(basePath+'RFdecision_dis4.pkl')
    modelRF5 = joblib.load(basePath+'RFdecision_dis5.pkl')
    modelRF6 = joblib.load(basePath+'RFdecision_dis6.pkl')
    modelRF7 = joblib.load(basePath+'RFdecision_dis7.pkl')
    
  
    # 将待决策数据分为只有取或者送的单和既有取又有送的单  
    trainData_sigle = trainData.loc[(trainData['取单号'] ==0) | (trainData['送单号'] ==0),:]  # 只有一边有订单
    trainData_double = trainData.loc[(trainData['取单号'] !=0) & (trainData['送单号'] !=0),:] # 两边都有订单
    
    # 只有一种单时，直接选该订单
    trainData_sigle['决策'] = trainData_sigle['取单号'].apply(lambda x :0 if x!= 0 else 1)
   
    # 有2种订单情况下，分为距离差在 dis范围外的和在dis范围内
    trainData_double_part1 = trainData_double.loc[(trainData_double['距离差'] <=dis)&(trainData_double['距离差'] >=-dis),:] 
    trainData_double_part2 = trainData_double.loc[(trainData_double['距离差'] <-dis)|(trainData_double['距离差'] > dis),:]
    
    # 距离差在dis范围外的，直接选择距离比较近的订单
    trainData_double_part2['决策'] = trainData_double_part2['距离差'].apply(lambda x: 0 if x <0 else 1)
    
    trainData_double_part1.reset_index(drop =True,inplace =True)
    
    
    # 距离差在dis范围内，根据模型进行决策
    for i in range(len(trainData_double_part1)):
        dis = trainData_double_part1.loc[i,'距离差']
        time1 = trainData_double_part1.loc[i,'理论时间差']
        time2 = trainData_double_part1.loc[i,'承诺时间差']
        time3 = trainData_double_part1.loc[i,'可取理论时间差']
        time4 = trainData_double_part1.loc[i,'可取单数']
        input1 = np.array([[time1,time2,time3,time4]])
        
        #根据距离差不同，采用相应的模型进行决策
        if (dis>=0) &(dis<=100):
            outputs = int(modelRF1.predict(input1)[0])
        elif (dis>=100)&(dis<=300):
            outputs = int(modelRF2.predict(input1)[0])
        elif dis>=300:
            outputs = int(modelRF3.predict(input1)[0])
        elif (dis>=-1201)&(dis<=-400):
            outputs = int(modelRF4.predict(input1)[0])
        elif (dis>=-400)&(dis<=-200):
            outputs = int(modelRF5.predict(input1)[0])
        elif (dis>=-200)&(dis<=-100):
            outputs = int(modelRF6.predict(input1)[0])
        else:
            outputs = int(modelRF7.predict(input1)[0])
        

        trainData_double_part1.loc[i,'决策'] = outputs
    
    # 合并数据
    dataSave = pd.concat([trainData_sigle,trainData_double_part1,trainData_double_part2])
    
    # 将数据整理成提交要求的格式
    dataPick = dataSave.loc[dataSave['决策'] ==0,['骑手ID','波次','取单号','起始经度','起始纬度','动作','理论取单时间']]
    dataDelivery = dataSave.loc[dataSave['决策'] ==1,['骑手ID','波次','送单号','起始经度','起始纬度','动作','理论送单时间']]
    
    dataPick['动作'] = 'PICKUP'
    dataDelivery['动作'] = 'DELIVERY'
    
    dataPick.rename(columns={'骑手ID':'courier_id','波次':'wave_index','取单号':'tracking_id','起始经度':'courier_wave_start_lng','起始纬度':'courier_wave_start_lat','动作':'action_type','理论取单时间':'expect_time'},inplace=True)
    dataDelivery.rename(columns={'骑手ID':'courier_id','波次':'wave_index','送单号':'tracking_id','起始经度':'courier_wave_start_lng','起始纬度':'courier_wave_start_lat','动作':'action_type','理论送单时间':'expect_time'},inplace=True)
    
    data = pd.concat([dataPick,dataDelivery])
    # 预测的行为完成时间 = 计算的理论时间+180(180是根据统计平均值得到的)
    data['expect_time'] = data['expect_time']+180
    data.loc[:,'courier_wave_start_lng'] = data.loc[:,'courier_wave_start_lng'].apply(XiaoShu)
    data.loc[:,'courier_wave_start_lat'] = data.loc[:,'courier_wave_start_lat'].apply(XiaoShu)
    
    return data

def main():
    # 数据读取
    data_list= [str(i) for i in range(20200301,20200307)]
    testDataSave=list()
    for i in data_list:
        df = pd.read_csv('../user_data/tmp_data/decision_'+i+'.txt')
        testDataSave.append(df)

    # 预测
    for i in range(len(testDataSave)):
        dataSave = DesicisonModel(testDataSave[i])
        dataSave.to_csv('../action_predict/'+'action_'+data_list[i]+'.txt',index =False,encoding='utf-8')

if __name__ == "__main__":
    
    main()
