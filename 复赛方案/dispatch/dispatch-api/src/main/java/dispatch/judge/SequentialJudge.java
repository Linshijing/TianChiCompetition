package dispatch.judge;

import com.google.common.collect.Iterables;
import com.google.common.collect.Lists;
import com.google.common.collect.Queues;
import dispatch.api.DispatchClient;
import dispatch.api.dto.*;
import lombok.Getter;

import java.util.ArrayList;
import java.util.List;
import java.util.Queue;

public class SequentialJudge {
    private DispatchClient dispatchClient;
    private int intervalSecond;

    private RawData rawData;
    private Queue<Order> orderQueue;
    private Queue<Courier> courierQueue;

    private long currentTime;
    private long endTime;

    @Getter
    private Score score;
    private List<DispatchLog> dispatchLogs = new ArrayList<>(0);


    public SequentialJudge(DispatchClient client, RawData rawData) {
        this(client, rawData, 60);
    }

    public SequentialJudge(DispatchClient client, RawData rawData, int intervalSecond) {
        this.dispatchClient = client;
        this.rawData = rawData;
        this.intervalSecond = intervalSecond;
        this.orderQueue = Queues.newArrayDeque(rawData.getOrders());
        this.courierQueue = Queues.newArrayDeque(rawData.getCouriers());
        this.score = new Score();

        this.currentTime = orderQueue.element().getCreateTime() + intervalSecond;
        this.endTime = Iterables.getLast(rawData.getOrders()).getCreateTime();

    }

    public void doDispatch() {
        DispatchContext dispatchContext = new DispatchContext();
        boolean isFirstRound = true;
        while (currentTime <= endTime) {
            DispatchRequest request = new DispatchRequest()
                    .setAreaId(rawData.getAreaId())
                    .setRequestTime(currentTime);

            List<Order> dispatchingOrders = Lists.newArrayList();
            List<Courier> onlineCourier = Lists.newArrayList();
            while (!orderQueue.isEmpty() && orderQueue.element().getCreateTime() <= currentTime) {
                dispatchingOrders.add(orderQueue.remove());
            }
            while (!courierQueue.isEmpty() &&
                    rawData.getCourierOnlineTime().get(courierQueue.element().getId()) <= currentTime) {
                onlineCourier.add(courierQueue.remove());
            }

            request.setCouriers(onlineCourier);
            request.setOrders(dispatchingOrders);

            currentTime += intervalSecond;
            request.setFirstRound(isFirstRound);
            request.setLastRound(currentTime > endTime);

            if (isFirstRound) {
                isFirstRound = false;
            }

            Response<DispatchSolution> solutionResponse;
            try {
                solutionResponse = dispatchClient.dispatch(request);
            } catch (Exception e) {
                score.setIllegalMsg(e.getMessage());
                return;
            }

            if (null == solutionResponse) {
                score.setIllegalMsg("no response");
                return;
            } else if (solutionResponse.getCode() != 200) {
                score.setIllegalMsg(solutionResponse.getMessage());
                return;
            } else {
                DispatchLog dispatchLog = new DispatchLog(request, solutionResponse.getResult());
                this.dispatchLogs.add(dispatchLog);
                IllegalMsg illegalMsg = dispatchContext.allocate(dispatchLog);
                if (illegalMsg.isIllegal()) {
                    score.setIllegalMsg(illegalMsg.getMsg());
                    return;
                }
            }
        }
        this.score = dispatchContext.checkAndScore();
    }
}
