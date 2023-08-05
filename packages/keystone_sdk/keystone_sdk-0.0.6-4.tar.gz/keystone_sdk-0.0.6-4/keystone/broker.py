# coding=utf-8

from __future__ import print_function
from six import with_metaclass
import abc
from datetime import datetime
import numpy as np

from keystone.api import keystone_class, api_method
import keystone.utils
from keystone.commission import KSCommissionModel
from keystone.slippage import KSSlippageModel
from keystone.constant import ORDER_ACCEPTED_MESSAGE, ORDER_FILLED_MESSAGE, ORDER_PARTIALLY_FILLED_MESSAGE
from keystone.order import (
                            KSTransaction, 
                            KSOrder,
                            KSOrderState,
                            KSOrderType,
                            KSOrderEvent,
                            KSOrderEventType
                            )
 

class KSBrokerPolicy(with_metaclass(abc.ABCMeta)):
    '''
    broker policy
    DO NOT use this class directlly
    '''
    def __init__(self, isInstantMatch = False, slippage = None, commission = None):
        self.isInstantMatch = isInstantMatch
        self.slippage = slippage
        self.commission = commission
        
    def useSlippageModel(self, model):
        if not issubclass(model, KSSlippageModel):
            raise TypeError("slippage model必须是继承自'KSSlippageModel'的实例对象。")
        self.slippage = model
        
    def useCommissionModel(self, model):
        if not issubclass(model, KSCommissionModel):
            raise TypeError("commission model必须是继承自'KSCommissionModel'的实例对象。")
        self.commission = model
        
    def turnOnInstantMatch(self):
        self.isInstantMatch = True
        
    @abc.abstractmethod
    def matchOrder(self, dataEvent, order, *args, **kwargs):
        pass
    
class KSDefaultBrokerPolicy(KSBrokerPolicy):
    def __init__(self):
        KSBrokerPolicy.__init__(self)
        
    def matchOrder(self, dataEvent, order, *args, **kwargs):
        sid = order.securityId()
        shares = order.remaining()
        dealPrice = dataEvent.query(sid, 'price')
        if np.isnan(dealPrice):
            return None
        
        if self.slippage is not None:
            direction = np.sign(shares)
            slippagePerc = self.slippage.compute()
            dealPrice = dealPrice * (1+slippagePerc*direction)
        commission = 0
        if self.commission is not None:
            commission = self.commission.compute(shares = shares, price = dealPrice)
        
        return KSTransaction(dataEvent.time(), order.orderid(), sid, shares, dealPrice, commission)
    

class KSBacktestingBroker(object):
    def __init__(self, *args, **kwargs):
        self.openOrders = {}
        self.filledOrders = {}
        self.cancelledOrders = {}
        self.brokerPolicy = kwargs.pop('brokerPolicy', KSDefaultBrokerPolicy())
        self.universe = kwargs.pop('universe')
        self.portfolio = kwargs.pop('portfolio')
        self.coordinator = kwargs.pop('coordinator')
        self.lastEvent = None
    
    def onDataEvent(self, dataEvent):
        self.lastEvent = dataEvent
        self.processAllOpenOrders(dataEvent)
    
    def registerOrder(self, order):
        self.openOrders[order.orderid()] = order
        
    def unregisterOrder(self, order):
        orderid = order.orderid()
        if orderid in self.openOrders:
            if order.state() == KSOrderState.FILLED:
                self.filledOrders[orderid] = order
            elif order.state() == KSOrderState.CANCELLED:
                self.cancelledOrders[orderid] = order
            else:
                pass
            self.openOrders.pop(orderid)
            
    def isExpiredOrder(self, order):
        return order.acceptedAt() < self.universe.time()
    
    def processAllOpenOrders(self, dataEvent):
        sortedOrders = self.getSortedOpenOrders()
        for order in sortedOrders:
            self.processOrder(dataEvent, order)
            
    def processOrder(self, dataEvent, order): 
        orderid = order.orderid()
        # Step 1 - check order content
        # 如果今天该sid不能交易则返回。例如停牌
        dt = self.universe.getPriceUpdateTime(order.sid())
        if  dt is None or dt < self.universe.time():
            order.cancel(self.universe.time(), 'cannot trade for ' + order.sid() + ' in this time.')
            self.unregisterOrder(order)
            self.notifyOrderEvent(orderid, KSOrderEventType.CANCELLED, order.cancelReason(), None)
            return
        
        if order.total() == 0:
            order.cancel(self.universe.time(), 'cannot place zero quantity order for ' + order.sid() + ' .')
            self.unregisterOrder(order)
            self.notifyOrderEvent(orderid, KSOrderEventType.CANCELLED, order.cancelReason(), None)
            return 
          
        # Step 2 - accept order
        if order.isSubmitted():
            order.accept(self.universe.time())
            self.notifyOrderEvent(orderid, KSOrderEventType.ACCEPTED, ORDER_ACCEPTED_MESSAGE, None)
            
        # Step 3 - check and remove expired order
        if self.isExpiredOrder(order):
            order.cancel(self.universe.time(), 'order expired')
            self.unregisterOrder(order)
            self.notifyOrderEvent(orderid, KSOrderEventType.CANCELLED, order.cancelReason(), None)
            return
        
        # Step 4 - simulating transaction
        txn = self.brokerPolicy.matchOrder(dataEvent, order)
        # txn validation
        if txn is None:
            order.cancel(self.universe.time(), 'user txn is None, cancel order.')
            self.unregisterOrder(order)
            self.notifyOrderEvent(orderid, KSOrderEventType.CANCELLED, order.cancelReason(), None)
            return
        
        # Step 5 - update order info
        order.update(txn)
        if order.isFilled():
            self.notifyOrderEvent(orderid, KSOrderEventType.FILLED, ORDER_FILLED_MESSAGE, txn)
        else:
            self.notifyOrderEvent(orderid, KSOrderEventType.PARTIALLY_FILLED, ORDER_PARTIALLY_FILLED_MESSAGE, txn)
            
        if order.isCancelled() or order.isFilled():
            self.unregisterOrder(order)
            
    def getSortedOpenOrders(self):
        openOrders = list(self.openOrders.values())
        datetimes = [x.submittedAt() for x in openOrders]
        idx = np.argsort(datetimes)
        return [openOrders[i] for i in idx]
    
    def notifyOrderEvent(self, orderid, type, message, txn):
        orderEvent = KSOrderEvent(orderid, type, message, txn)
        self.coordinator.dispatchOrderEvent(orderEvent)
        
    def getOrder(self, orderid):
        if orderid in self.openOrders:
            return self.openOrders[orderid]
        elif orderid in self.filledOrders:
            return self.filledOrders[orderid]
        elif orderid in self.cancelledOrders:
            return self.cancelledOrders[orderid]
        else:
            return None
        
    def submitOrder(self, sid, quantity, type = KSOrderType.MARKET_ORDER):
        order = KSOrder(sid, quantity, type)
        order.submit(self.universe.time())
        self.registerOrder(order)
        
        if self.brokerPolicy.isInstantMatch:
            self.processOrder(self.lastEvent, order)
            
        return order.orderid()
    
    def order(self, sid, quantity, type = KSOrderType.MARKET_ORDER):
        return self.submitOrder(sid, quantity, type)
    
    def orderValue(self, sid, value, type = KSOrderType.MARKET_ORDER):
        price = self.universe.getPrice(sid)
        shares = np.floor(np.abs(value) / price)*np.sign(value)
        return self.submitOrder(sid, shares, type)
    
    def orderPercentage(self, sid, percentage, type = KSOrderType.MARKET_ORDER):
        return self.orderValue(sid, self.portfolio.value() * percentage, type)
    
    def orderTarget(self, sid, targetShares, type = KSOrderType.MARKET_ORDER):
        curShares = 0
        if self.portfolio.hasPosition(sid):
            curShares = self.portfolio.getPosition(sid).quantity()
        return self.submitOrder(sid, targetShares - curShares, type)
        
    def orderTargetValue(self, sid, targetValue, type = KSOrderType.MARKET_ORDER):
        curValue = 0
        if self.portfolio.hasPosition(sid):
            curValue = self.portfolio.getPosition(sid).value()
        return self.orderValue(sid, targetValue - curValue, type)
    
    def orderTargetPercentage(self, sid, percentage, type = KSOrderType.MARKET_ORDER):
        return self.orderTargetValue(sid, self.portfolio.value() * percentage, type)
    
    def cancelOrder(self, orderid):
        if orderid in self.openOrders:
            order = self.openOrders[orderid]
            order.cancel(self.universe.time(), "cancelled by user")
            self.unregisterOrder(order)