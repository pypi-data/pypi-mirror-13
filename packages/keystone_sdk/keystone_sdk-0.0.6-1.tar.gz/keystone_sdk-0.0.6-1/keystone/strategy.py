# -*- coding: utf-8 -*-

from __future__ import print_function
import inspect
from six import with_metaclass
import abc
import numpy as np
from datetime import datetime

import keystone.parameters
import keystone.utils
from keystone.api import keystone_class, api_method
from keystone.coordinator import KSObserver, KSCoordinator
from keystone.sources import KSCsvSource, KSMemorySource
from keystone.portfolio import KSPortfolio
from keystone.universe import KSUniverse
from keystone.broker import KSBacktestingBroker, KSBrokerPolicy, KSDefaultBrokerPolicy
from keystone.action import KSContext, KSAction
from keystone.order import KSOrderEventType
from keystone.history import KSHistory
from keystone.exception import KSStopLineReachedException, KSEndTimeReachedException
from keystone.performance.perf import KSPerformance, PeriodReturn
from keystone.performance.analyzer import KSAnalyzer, KSSampleRate
from keystone.app_client.drain import Drain
from keystone.app_client.datetime_breakpoint import DatetimeBreakpoint
from keystone.py3compat import PY3, builtin_mod, iteritems, unicode_type, string_types
    
class KSStrategy(with_metaclass(abc.ABCMeta)):
    '''
    User strategy base class
    DO NOT use this class directly.

    _datetimeBreakPointCls is used by KPdb to set datetime breakpoints
    '''
    _datetimeBreakPointCls = DatetimeBreakpoint

    @abc.abstractmethod
    def onData(self, data, context, action):
        pass
    
    def onBeforeData(self, data, context, action):
        pass
    
    def onOrderEvent(self, orderEvent):
        pass
    

class KSStrategyManager(KSObserver):
    '''
    strategy Manager
    '''
    def __init__(self, 
                 strategyClass, 
                 universe,
                 portfolio, 
                 broker,
                 history,
                 analyzers,
                 perf,
                 startTime,
                 endTime,
                 stopLossPercentage):
        KSObserver.__init__(self)
        self.strategy = strategyClass()
        self.portfolio = portfolio
        self.context = KSContext(portfolio, history, analyzers, universe)
        self.action = KSAction(broker)
        self.startTime = startTime
        self.endTime = endTime
        self.stopLossPercentage = 0.0
        self.perf = perf
        self.analyzers = analyzers
    
    def onDataEvent(self, dataEvent):
        if self.strategy is None:
            return
        
        if dataEvent.time() < self.startTime:
            self.strategy.onBeforeData(dataEvent, self.context, self.action)
        elif dataEvent.time() > self.endTime:
            raise KSEndTimeReachedException()
        else:
            self.strategy.onData(dataEvent, self.context, self.action)
            # update performance
            self.perf.update(dataEvent, self.context)
            # update analyzer
            for analyzer in self.analyzers:
                analyzer.update(dataEvent, self.context)
        
        if self.portfolio.value() / self.portfolio.startingCash() < self.stopLossPercentage:
            raise KSStopLineReachedException()
        
    def onOrderEvent(self, orderEvent):
        if orderEvent.type != KSOrderEventType.ACCEPTED and orderEvent.type != KSOrderEventType.CANCELLED:
            self.updatePortfolio(orderEvent)
            
        if self.strategy is not None:
            self.strategy.onOrderEvent(orderEvent)
    
    def updatePortfolio(self, orderEvent):
        txn = orderEvent.txn
        self.portfolio.update(txn.sid, txn.quantity, txn.price, txn.commission)
        
    
class KSStrategyRunner(object):
    '''
    strategy runner
    '''
    def __init__(self):
        self.strategyClass = None
        self.sources = []
        self.analyzers = []
        self.history = None
        self.brokerPolicy = KSDefaultBrokerPolicy() 
        self.startingCash = keystone.parameters.DEFAULT_STARTING_CASH
        self.startTime = datetime.min
        self.endTime = datetime.max
        self.stopLossPercentage = keystone.parameters.DEFAULT_STOPLOSS_PERENTAGE
        self.drainAddress = None
        self.synAddress = None
        self.universe = KSUniverse()
        self.perf = KSPerformance()
    
    
    def addSource(self, source):
        if not isinstance(source, KSCsvSource) and not isinstance(source, KSMemorySource):
            raise TypeError("source必须为'KSCsvSource'或'KSMemorySource'对象。")
        self.sources.append(source)
        
    
    def setCash(self, cash):
        if not keystone.utils.isnumber(cash):
            raise TypeError("cash必须为数字。")
        self.startingCash = cash
        
    
    def setStartTime(self, startTime):
        if not isinstance(startTime, datetime):
            raise TypeError("startTime必须为'datetime'类型。")
        
        if self.endTime < startTime:
            raise TypeError("startTime不可大于endTime。")
        
        self.startTime = startTime
        
    
    def setEndTime(self, endTime):
        if not isinstance(endTime, datetime):
            raise TypeError("endTime必须为'datetime'类型。")
        
        if endTime < self.startTime:
            raise TypeError("endTime不可小于startTime。")
        
        self.endTime = endTime
        
    def setStopPercentage(self, percentage):
        if not keystone.utils.isnumber(percentage) or percentage < 0.0 or percentage > 1.0:
            raise TypeError("percentage必须满足 0 <= percentage <= 1")
        
        self.stopLossPercentage = percentage
    
    
    def setStrategy(self, strategy):
        if not issubclass(strategy, KSStrategy):
            raise TypeError("strategy必须为继承自'keystone.strategy.KSStrategy'的子类。")
        
        self.strategyClass = strategy
        
    
    def setBrokerPolicy(self, brokerPolicy):
        if not isinstance(brokerPolicy, KSBrokerPolicy):
            raise TypeError("brokerPolicy必须为继承自'keystone.broker.KSBrokerPolicy'的子类实例对象.")
        self.brokerPolicy = brokerPolicy
        
    
    def attachAnalyzer(self, analyzer):
        if not isinstance(analyzer, KSAnalyzer):
            raise TypeError("analyzer必须为继承自'keystone.performance.analyzer.KSAnalyzer'的子类实例对象。")
        self.analyzers.append(analyzer)
    
    
    def setHistoryCapacity(self, capacity):
        if not keystone.utils.isnumber(capacity):
            raise TypeError("capacity必须为整数。")
        self.history = KSHistory(capacity)
        
    def setDrainAddress(self, address, synAddress):
        self.drainAddress = address
        self.synAddress = synAddress

    def setBenchmark(self, column, sid=[]):
        if sid != [] and not isinstance(sid, unicode_type):
            raise TypeError("sid必须为字符串。")
        if not isinstance(column, unicode_type):
            raise TypeError("column必须为字符串。")
        PeriodReturn.setBenchmark(sid, column)

    def setSampleRate(self, sampleRate):
        if sampleRate not in [KSSampleRate.MONTH, KSSampleRate.DAY, KSSampleRate.MINUTE, KSSampleRate.HOUR, KSSampleRate.SECOND]:
            raise TypeError("sampleRate格式错误。")
        self.perf.setSampleRate(sampleRate)

    def setRiskless(self, riskless):
        if not keystone.utils.isnumber(riskless):
            raise TypeError("riskless必须为整数。")
        self.perf.setRiskless(riskless)

    def setTradingDays(self, days):
        if not keystone.utils.isnumber(days):
            raise TypeError("days必须为整数。")
        self.perf.setTradingDays(days)

    def setTradingHours(self, hours):
        if not keystone.utils.isnumber(hours):
            raise TypeError("hours必须为整数。")
        self.perf.setTradingHours(hours)

    def run(self):
        if self.strategyClass is None:
            raise ValueError("can not find user strategy")
        # Initialize Coordinator and add user sources
        coordinator = KSCoordinator()
        for source in self.sources:
            coordinator.eventEngine.addSource(source)
            
        # Initialize Universe
        universe = self.universe
        
        # Initialize Portfolio
        portfolio = KSPortfolio(self.startingCash, universe)
        
        # Initialize Broker
        broker = KSBacktestingBroker(universe = universe, 
                                     portfolio = portfolio,
                                     coordinator = coordinator,
                                     brokerPolicy = self.brokerPolicy)
        
        # Initialize Strategy Manager
        strategyManager = KSStrategyManager(self.strategyClass,
                                            universe,
                                            portfolio,
                                            broker,
                                            self.history,
                                            self.analyzers,
                                            self.perf,
                                            self.startTime,
                                            self.endTime,
                                            self.stopLossPercentage)
        
        # Initialize drain
        self.drain = None
        if self.drainAddress is not None:
            self.drain = Drain(strategyManager, drain_url=self.drainAddress, syn_url=self.synAddress)
            self.drain.start()

        # NOTE: add observer, order matters
        coordinator.addDataObserver(universe)
        coordinator.addDataObserver(broker)
        coordinator.addDataObserver(strategyManager)
        if self.history is not None:
            coordinator.addDataObserver(self.history)
        if self.drain is not None:
            coordinator.addDataObserver(self.drain)
            
        coordinator.addOrderObserver(strategyManager)
        if self.drain is not None:
            coordinator.addOrderObserver(self.drain)
        
        # run
        try:
            coordinator.run()
        except KSEndTimeReachedException:
            pass
        except KSStopLineReachedException:
            print("已达止损线，回测将自动停止。")
            
        if self.drain is not None:
            self.drain.wait()
