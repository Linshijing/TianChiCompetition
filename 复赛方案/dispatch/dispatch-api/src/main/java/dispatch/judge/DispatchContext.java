package dispatch.judge;

import com.google.common.collect.Maps;
import dispatch.api.dto.*;
import lombok.Getter;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Getter
public class DispatchContext {
    private Map<String, CourierRecord> courierRecordMap;
    private Map<String, OrderRecord> orderRecordMap;

    public DispatchContext() {
        this.courierRecordMap = Maps.newHashMap();
        this.orderRecordMap = Maps.newHashMap();
    }

    public IllegalMsg allocate(DispatchLog dispatchLog) {
        DispatchRequest request = dispatchLog.getRequest();
        request.getOrders().forEach(o -> orderRecordMap.put(o.getId(), new OrderRecord(o)));
        request.getCouriers().forEach(c -> courierRecordMap.put(c.getId(), new CourierRecord(c, request.getRequestTime())));
        courierRecordMap.values().forEach(courierRecord -> courierRecord.timeChange(request.getRequestTime()));

        DispatchSolution solution = dispatchLog.getSolution();


        for (CourierPlan courierPlan : solution.getCourierPlans()) {
            CourierRecord courierRecord = courierRecordMap.get(courierPlan.getCourierId());
            for (ActionNode actionNode : courierPlan.getPlanRoutes()) {
                OrderRecord orderRecord = orderRecordMap.get(actionNode.getOrderId());
                Order order = orderRecord.getOrder();
                Location actionLoc = actionNode.getActionType() == 3 ? order.getDstLoc() : order.getSrcLoc();

                if (!orderStatusCheck(orderRecord, actionNode)) {
                    return new IllegalMsg("错误的订单状态");
                }
                if (!orderPickTimeCheck(orderRecord, actionNode)) {
                    return new IllegalMsg("在出餐时间前取餐");
                }
                if (!canArrive(courierRecord, actionLoc, actionNode.getActionTime())) {
                    return new IllegalMsg("骑手无法在指定时间到达");
                }

                orderRecord.setStatus(actionNode.getActionType());
                if (actionNode.getActionType() == 3) {
                    orderRecord.setOverTime(actionNode.getActionTime() > order.getPromiseDeliverTime());
                    orderRecord.setDeliveryTime(actionNode.getActionTime() - orderRecord.getOrder().getCreateTime());
                }
                courierRecord.timeChange(actionNode.getActionTime());
                courierRecord.setLocation(actionLoc);
            }
        }
        return new IllegalMsg();
    }

    public Score checkAndScore() {
        Score score = new Score();
        if (!checkAllOrderCompeted()) {
            score.setIllegalMsg(new IllegalMsg("有订单未配送完成"));
        } else if (!checkCourierLoad()) {
            score.setIllegalMsg(new IllegalMsg("超骑士最大背单量"));
        } else {
            int overTimeCount = (int) orderRecordMap.values().stream().filter(OrderRecord::isOverTime).count();
            long serviceTimeSum = orderRecordMap.values().stream().mapToLong(OrderRecord::getDeliveryTime).sum();
            long orderSum = orderRecordMap.size();
            score.setOrderSum(orderSum);
            score.setAvgServiceTime(serviceTimeSum * 1. / orderSum);
            score.setOvertimeCount(overTimeCount);
            score.setServiceTimeSum(serviceTimeSum);
        }
        return score;
    }

    /** 所有订单都完成 */
    private boolean checkAllOrderCompeted() {
        return orderRecordMap.values().stream().allMatch(o -> o.getStatus() == 3);
    }

    /** 背单量检查 */
    private boolean checkCourierLoad() {
        return courierRecordMap.values().stream().allMatch(courierRecord -> {
            List<ActionNode> actionNodes = courierRecord.getCourierPlans().stream()
                    .flatMap(courierPlan -> courierPlan.getPlanRoutes().stream())
                    .collect(Collectors.toList());
            int cr = 0;
            int maxCr = 0;
            for (ActionNode node : actionNodes) {
                if (node.getActionType() == 2) {
                    maxCr = Math.max(maxCr, ++cr);
                }
                if (node.getActionType() == 3) {
                    --cr;
                }
            }
            return maxCr <= courierRecord.getCourier().getMaxLoads();
        });
    }

    /** 订单状态转移检查 */
    private boolean orderStatusCheck(OrderRecord orderRecord, ActionNode actionNode) {
        // 状态递增 或者 从 到店到第二次到店
        return (actionNode.getActionType() == orderRecord.getStatus() + 1 || (orderRecord.getStatus() == 1 && actionNode.getActionType() == 1))
                && actionNode.getActionType() <= 3;
    }

    /** 取餐时间检查 */
    private boolean orderPickTimeCheck(OrderRecord orderRecord, ActionNode actionNode) {
        // 取餐时间需要不早于预计出餐时间
        return actionNode.getActionType() != 2 || actionNode.getActionTime() >= orderRecord.getOrder().getEstimatedPrepareCompletedTime();
    }

    /** 到达时间检查 */
    private boolean canArrive(CourierRecord courierRecord, Location actionLoc, Long actionTime) {
        long useTime = actionTime - courierRecord.getCourierTime();
        return useTime * courierRecord.getCourier().getSpeed() >= JudgeUtil.getDistance(courierRecord.getLocation(), actionLoc);
    }
}
