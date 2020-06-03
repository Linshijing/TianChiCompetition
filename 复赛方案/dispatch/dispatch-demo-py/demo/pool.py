from .dto import Order, Courier
from typing import Dict, List


class OrderPool:
    def __init__(self):
        self.orders: List[Order] = []
        self.orderMap: Dict[str, Order] = {}

    def addDispatchingOrders(self, dispatchingOrders: List[Order]):
        self.orders = self.orders + dispatchingOrders
        for order in dispatchingOrders:
            self.orderMap[order.id] = order

    def getDispatchingOrders(self):
        return [order for order in self.orders if order.status == 0]

    def markAssignedOrder(self, orderId):
        self.orderMap.get(orderId).setStatus(1)

    def markArrivalCompleteOrder(self, orderId):
        self.orderMap.get(orderId).setStatus(2)

    def markPickCompleteOrder(self, orderId):
        self.orderMap.get(orderId).setStatus(3)

    def markDeliverCompleteOrder(self, orderId):
        self.orderMap.get(orderId).setStatus(4)

    def getOrder(self, orderId) -> Order:
        return self.orderMap.get(orderId)


class CourierPool:
    def __init__(self):
        self.couriers: List[Courier] = []

    def addOnlineCouriers(self, courierList: List[Courier]):
        self.couriers.extend(courierList)

