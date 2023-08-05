# -*- coding: utf-8 -*-

from __future__ import print_function
from keystone.api import keystone_class, api_method
from datetime import datetime
import numpy as np
from keystone.coordinator import KSObserver

class KSUniverse(KSObserver):
    '''
    Universe infomations about security and current backtesting time
    '''
    time = None
    price = {}
    priceUpdateTime = {}
    latestDataEvent = None
    def __init__(self):
        KSObserver.__init__(self)
    
    @classmethod
    def getPriceUpdateTime(cls, security):
        if security in cls.priceUpdateTime:
            return cls.priceUpdateTime[security]
        else:
            return None
        
    @classmethod
    def getPrice(cls, security):
        if security in cls.price:
            return cls.price[security]
        else:
            return np.nan
    
    @classmethod
    def onDataEvent(cls, dataEvent):
        # update time
        cls.time = dataEvent.time()
        
        # update latest dataEvent
        cls.latestDataEvent = dataEvent
        
        # update price
        securities = dataEvent.securities()
        if len(securities) == 0:
            return
        latestPrice = dataEvent.query(securities, 'price')
        if len(securities) == 1:
            cls.price[securities[0]] = latestPrice
            cls.priceUpdateTime[securities[0]] = cls.time
        else:
            cls.price.update(latestPrice.to_dict())
            cls.priceUpdateTime.update({x:cls.time for x in latestPrice.index})