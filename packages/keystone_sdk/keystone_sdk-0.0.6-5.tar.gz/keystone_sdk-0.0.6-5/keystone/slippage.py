# -*- coding: utf-8 -*-

from __future__ import print_function
from six import with_metaclass
import abc
import numpy as np
from datetime import datetime

from keystone.api import keystone_class, api_method
import keystone.utils

class KSSlippageModel(with_metaclass(abc.ABCMeta)):
    def __init__(self):
        pass
    
    @abc.abstractmethod
    def compute(self, *args, **kwargs):
        return 0
    
class KSFixedSlippageModel(KSSlippageModel):
    def __init__(self, rate):
        KSSlippageModel.__init__(self)
        if not keystone.utils.isnumber(rate) or rate < 0 or rate > 1:
            raise TypeError("rate必须为数字，且 0 <= rate <= 1。")
        self.__spread = rate
    
    def compute(self, *args, **kwargs):
        return self.__spread/2