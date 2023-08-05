# -*- coding: utf-8 -*-

from __future__ import print_function
import time
import pandas as pd
import sys
from six import with_metaclass
import abc

from keystone.api import keystone_class, api_method
from keystone.engine import KSEventEngine

class KSObserver(with_metaclass(abc.ABCMeta)):
    
    @abc.abstractmethod
    def onDataEvent(self, dataEvent):
        pass
    
    def onOrderEvent(self, orderEvent):
        pass
    

class KSCoordinator(object):
    def __init__(self):
        # pass pd.DataFrame function handle to KSEventEngine
        # enable cpp interface KSDataEvent.query call pd.DataFrame
        # function and return a pd.DataFrame object 
        # self.eventEngine = KSEventEngine(pd.DataFrame)
        self.eventEngine = KSEventEngine(pd.Series)
        self.dataObservers = []
        self.orderObservers = []
    
    def addDataObserver(self, observer):
        self.dataObservers.append(observer)
        
    def addOrderObserver(self, observer):
        self.orderObservers.append(observer)
        
    def dispatchDataEvent(self, dataEvent):
        for observer in self.dataObservers:
            observer.onDataEvent(dataEvent)
            
    def dispatchOrderEvent(self, orderEvent):
        for observer in self.orderObservers:
            observer.onOrderEvent(orderEvent)
            
    def run(self):
        self.eventEngine.run();
        while 1:
            dataEvent = self.eventEngine.getNextEvent()
            if dataEvent is None:
                break
            else:
                self.dispatchDataEvent(dataEvent)
            