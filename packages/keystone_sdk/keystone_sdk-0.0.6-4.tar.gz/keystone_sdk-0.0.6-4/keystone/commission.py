# -*- coding: utf-8 -*-

from __future__ import print_function
from six import with_metaclass
import abc
import numpy as np
from datetime import datetime

from keystone.api import keystone_class, api_method
import keystone.utils

class KSCommissionModel(with_metaclass(abc.ABCMeta)):
    def __init__(self):
        pass
    
    @abc.abstractmethod
    def compute(self, *args, **kwargs):
        return 0
    
class KSPerShareCommissionModel(KSCommissionModel):
    def __init__(self, rate):
        KSCommissionModel.__init__(self)
        if not keystone.utils.isnumber(rate):
            raise TypeError("rate必须为数字。")
        self.__rate = rate
        
    def compute(self, *args, **kwargs):
        return abs(kwargs['shares']) * self.__rate
    
class KSTransactionValueCommissionModel(KSCommissionModel):
    def __init__(self, rate):
        KSCommissionModel.__init__(self)
        if not keystone.utils.isnumber(rate):
            raise TypeError("rate必须为数字。")
        self.__rate = rate
    
    def compute(self, *args, **kwargs):
        return abs(kwargs['shares'] * kwargs['price'] * self.__rate)