# 智慧物流运单调度比赛
## 更新日志

## 背景
balabala

## 比赛说明
### 架构
![](deploy.png)

- 参赛选手程序和评测打分程序运行在同一个容器内(8C16G规格，无对外公网访问，磁盘大小有限制)
- 参赛选手程序和评测打分程序共享容器总资源（包括CPU，内存和磁盘）

### 程序交互说明
1. 评测程序发送POST /api/v1/dispatch请求给选手Server，输入某一商圈（areaId）本轮新增待指派运单，本轮新上线骑手，每一个商圈的第一次指派，请求体中的isFirstRound=true，否则都为false。
2. 选手程序经过计算，返回经过本轮指派之后，骑手最新的路径规划。
3. 业务时间戳往后移动1分钟，重复以上第1，2步，直到推送当前商圈最后一批待指派订单时，请求体中的isLastRound=true，否则都为false。
4. 重复以上1，2，3步骤，直到完成所有商圈的指派。

### 参赛选手程序要求
1. 提供一个Restful Server，监听本地：http://localhost:8080, 端口不能修改
2. 程序使用的最大内存不能超过13g，以保证评测打分程序所需之必要资源，同理，CPU资源也需要注意预留资源给评测打分系统
3. 程序必须在10s之内启动，超过5s评测程序访问选手程序无响应，成绩为0。

### 参赛选手程序Server响应要求
1. 每个API的响应时间必须满足响应时间要求，否则得分为0。
2. 对于评测程序的每一次请求，都需响应，超时或抛出异常或则code!=200，得分为0。

## 参赛选手程序提供的Restful API说明
### 1. ping
#### 作用
```
提供给评测程序用来探测选手程序进程状态
```
#### URL
```
/api/v1/ping
```
#### HTTP请求方式
```
GET
```
#### 请求参数
```
无
```

#### 返回字段
| 返回字段      | 字段类型      | 说明                                  |
| -------------| -------------|---------------------------------------|
| code         | int          | 请求状态，200表示正常，500表示服务端内部错误  | 
| result       | string/object  | 服务端返回的请求结果 ，在PING API中为,result为"PONG"          |                     
| message      | string       | code非200时，表示服务端错误原因         | 

#### 例子
```
{"code":200,"result":"PONG","message":null}
```

#### 响应时间要求
```
<=100ms
```

### 2. dispatch
#### 作用
```
推送待指派运单和在线骑手供选手进行调度指派，选手程序经过计算以后，需要返回经过本轮指派之后所有骑手的取餐和送餐的路径规划
注意：后面轮次指派之后的路径规划不能覆盖前面轮次的规划，即后面轮次新指派之后，每个骑手之前轮次规划不能进行修改修改，只能在数组后面追加最新指派之后骑手新的路径规划结果
```
#### URL
```
/api/v1/dispatch
```
#### HTTP请求方式
```
POST
```
#### 请求Header
```
Content-type: application/json;charset=utf-8;
```


#### 请求字段
| 请求字段 | 字段类型| 说明|
| --------| -------------|--------|
| requestTimestamp      | long         | 本轮调度系统时间戳(Unix Timestamp)                                                   | 
| areaId                | string        | 商圈ID                                                          |                     
| isFirstRound          | boolean      | 是否当前商圈第一波订单，每个商圈第一次请求为true，之后都为false        | 
| isLastRound           | boolean      | 是否当前商圈最后一波订单，每个商圈最后一次请求为true，之前都为false        | 
| couriers              | List&lt;Courier&gt;      | 当前时间戳新上线骑手，历史骑手选手自己保存     | 
| orders                | List&lt;Order&gt;    | 当前时间戳下新增运单，历史运单选手自己保存     | 

#### 例子
```json
{
    "areaId":"461159",
    "couriers":[//新增上线骑手列表
        {
            "areaId":"461159",
            "id":"1271846948",
            "loc":{//骑士所在位置
                "latitude":39.404385000000005,
                "longitude":93.714482
            },
            "maxLoads":9, //骑士最大负载值
            "speed":3.32024717311128 //骑士跑动速度
        },
        {
            "areaId":"461159",
            "id":"1565967952",
            "loc":{
                "latitude":39.394585,
                "longitude":93.71377899999999
            },
            "maxLoads":9,
            "speed":4.57578857050265
        }
    ],
    "firstRound":true,
    "lastRound":false,
    "orders":[//新增待指派运单列表
        {
            "areaId":"461159",
            "createTime":1271846948,
            "dstLoc":{//送货地
                "latitude":39.3921,
                "longitude":93.71659
            },
            "estimatedPrepareCompletedTime":1578441596,//预计取货地备货完成时间，骑手不能早于该时间点取货
            "id":"14700505841629255466",
            "promiseDeliverTime":1578443275,//期望送达时间
            "srcLoc":{//取货地
                "latitude":39.4032065165,
                "longitude":93.71392033250001
            }
,        }
    ],
    "requestTime":1578441056
}
```

#### 响应字段
| 返回字段      | 字段类型      | 说明                                  |
| -------------| -------------|--------|
| code         | int          | 请求状态，200表示正常，500服务端内部错误  | 
| result       | List&lt;DispatchSolution&gt;       | 本轮分单指派之后，骑手最新路径规划，DispatchSolution详细格式参看源代码       |                     
| message      | 字符串        | code非200时，表示服务端错误原因         | 
#### 例子
```json
{
    "code":200,
    "result":{
        "courierPlans":[
            {
                "courierId":"1271846948",
                "planRoutes":[
                    {
                        "actionTime":1578441458,//该动作发生时间
                        "actionType":1,//1:到店动作; 2.取餐动作; 3.送货动作
                        "orderId":"14700505841629255466"
                    }
                ]
            }
        ]
    }
}
```

#### 响应时间要求
```
<=5000ms
```

### 比赛镜像要求
1. CMD 必须是/data/run.sh，该脚本由选手自己提供（参考run.sh）。

### 本地调试
#### 本地有java&maven环境
1. 编译
```
make build-java
```
2. 启动选手自己http server，端口8080
3. 启动评测程序，进行评测
```
java -jar dispatch-api/target/dispatch-judge-jar-with-dependencies.jar /test_data_dir
```

#### 本地无java环境，使用Docker
1. 编译选手自己代码
```
make build-java # build-python,build-go
```
2. 启动选手自己http server，端口8080
3. 启动评测镜像
``` 
docker run -e API_SERVER="http://172.17.0.1:8080" -it registry.cn-hangzhou.aliyuncs.com/tianchi-eleme-dispatch/judge-base:v2.0
```

### Module说明
| Module      | 字段类型      | 
| -------------| -------------|
| dispatch-api | 官方评测程序，Java DTO等        | 
| dispatch-demo | Java版本的Http Server框架和Demo实现，选手可以任意实现，仅做参考 |                    
| dispatch-py | python版本简单Http Server框架，没有实现逻辑，选手可以任意修改   | 
| dispatch-go | go版本简单Http Server框架，没有实现逻辑，选手可以任意修改   | 

