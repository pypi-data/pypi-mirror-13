# -*- coding: utf-8 -*-

from functools import wraps
import keystone.api_allow_classes
import types
import keystone.utils

def keystone_class(original_class):
    keystone.api_allow_classes.__all__.append('.'.join([original_class.__module__, original_class.__name__]))
    for attr_name, attr_value in original_class.__dict__.items() :
        if not attr_name.startswith('__')  and isinstance(attr_value, types.FunctionType):
            setattr(original_class, attr_name, api_callable_check(attr_value))
    return original_class

def api_callable_check(func):
    '''
    api_callable_check decorator
    WARNNING: api_callable_check MUST BE the top decorator
    '''
    @wraps(func)
    def warpped(*args, **kwargs):
        if hasattr(func, 'is_api_method'):
            return func(*args, **kwargs)
        caller = keystone.utils.get_caller_name()
        caller_module = '.'.join(caller[:-1])
        if caller_module in keystone.api_allow_classes.__all__:
            return func(*args, **kwargs)
        else:
            raise NotImplementedError('function "' + func.__name__ + '" not implemented!')

    return warpped

def api_method(func):
    '''
    api method decorator
    '''
    @wraps(func)
    def warpped(*args, **kwargs):
        return func(*args, **kwargs)

    warpped.is_api_method = 1
    return warpped
