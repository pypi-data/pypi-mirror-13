# -*- coding: utf-8 -*-

from __future__ import print_function
from collections import deque, Iterable
import pandas as pd

import keystone.utils
from keystone.api import keystone_class, api_method
from keystone.coordinator import KSObserver
from keystone.py3compat import PY3, builtin_mod, iteritems, unicode_type, string_types
import datetime


class KSHistory(KSObserver):
    def __init__(self, capacity):
        if not keystone.utils.isint(capacity) or capacity == 0:
            raise TypeError("capacity格式错误，capacity必须为非0整数。")
        self.__capacity = capacity
        self.__data = deque([],capacity)
        
    
    def query(self, startTime, endTime, ids, fieldname):
        # print "[startTime,endTime] = [" + str(startTime) + "," + str(endTime) +"]"
        # Check parameters
        if not isinstance(startTime, datetime.datetime):
            raise TypeError("startTime格式错误，startTime必须为datetime类型。")
        
        if not isinstance(endTime, datetime.datetime):
            raise TypeError("endTime格式错误，endTime必须为datetime类型。")
        
        if not isinstance(fieldname, string_types):
            raise TypeError("fieldname格式错误, fieldname必须是字符串。")
        
        if not isinstance(ids, string_types) and not isinstance(ids, Iterable):
            raise TypeError("securities格式错误, securities必须是字符串或字符串数组。")
        
        if isinstance(ids, Iterable):
            for x in ids:
                if not isinstance(x, string_types):
                        raise TypeError("securities格式错误, securities必须是字符串或字符串数组。")
        
        # Query
        ret = pd.DataFrame()
        for dataEvent in self.__data:
            dt = dataEvent.time()
            if startTime <= dt and dt <= endTime:
                ret = ret.join(dataEvent.query(ids, fieldname), how = 'outer')
                
        return ret
    
    
    def queryN(self, n, ids, fieldname):
        # Check parameters
        if not keystone.utils.isint(n) or n == 0:
            raise TypeError("n格式错误，n必须为非0整数。")
        
        if not isinstance(fieldname, string_types):
            raise TypeError("fieldname格式错误, fieldname必须是字符串。")
        
        if not isinstance(ids, string_types) and not isinstance(ids, Iterable):
            raise TypeError("securities格式错误, securities必须是字符串或字符串数组。")
        
        if isinstance(ids, Iterable):
            for x in ids:
                if not isinstance(x, string_types):
                        raise TypeError("securities格式错误, securities必须是字符串或字符串数组。")
                    
        # QueryN
        ret = pd.DataFrame()
        m = min(n, len(self.__data))
        iter = range(len(self.__data) - m, len(self.__data))
        for i in iter:
            ret = ret.join(self.__data[i].query(ids, fieldname), how = 'outer')
            
        return ret
    
    def onDataEvent(self, dataEvent):
        self.__data.append(dataEvent)
    