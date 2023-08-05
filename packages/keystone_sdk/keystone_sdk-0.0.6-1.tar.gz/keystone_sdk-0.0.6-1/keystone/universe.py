# -*- coding: utf-8 -*-

from __future__ import print_function
from keystone.api import keystone_class, api_method
from datetime import datetime
import numpy as np
from keystone.coordinator import KSObserver


class KSUniverse(KSObserver):
    def __init__(self):
        KSObserver.__init__(self)
        self.__time = None
        self.__price = {}
        self.__priceUpdateTime = {}
        self.__latestDataEvent = None
        
    
    def latestData(self):
        return self.__latestDataEvent
    
    
    def time(self):
        return self.__time
    
    
    def getPriceUpdateTime(self, security):
        if security in self.__priceUpdateTime:
            return self.__priceUpdateTime[security]
        else:
            return None
        
    
    def getPrice(self, security):
        if security in self.__price:
            return self.__price[security]
        else:
            return np.nan
        
    def onDataEvent(self, dataEvent):
        # update time
        self.__time = dataEvent.time()
        
        # update latest dataEvent
        self.__latestDataEvent = dataEvent
        
        # update price
        securities = dataEvent.securities()
        if len(securities) == 0:
            return
        latestPrice = dataEvent.query(securities, 'price')
        if len(securities) == 1:
            self.__price[securities[0]] = latestPrice
            self.__priceUpdateTime[securities[0]] = self.__time
        else:
            self.__price.update(latestPrice.to_dict())
            self.__priceUpdateTime.update({x:self.__time for x in latestPrice.index})