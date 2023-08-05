# -*- coding: utf-8 -*-

# windows: set VS90COMNTOOLS=%VS120COMNTOOLS% python build.py build --boost-dir=../../lib/boost_1.58_win64 --event-engine-include=../../../ --event-engine-lib=../../lib/win64/
# mac: python setup.py install --boost-dir=../../lib/boost_1.58_mac --event-engine-include=../../../ --event-engine-lib=../../lib/mac/
from distutils.version import StrictVersion
from setuptools import (
    Extension,
    find_packages,
    setup,
)
from sys import platform as _platform
import sys
import copy

BOOST_HOME = 'boost'
EVENT_ENGINE_INCLUDE ='eventengine/include'
EVENT_ENGINE_LIB ='eventengine/lib'

BOOST_HOME_CMD = '--boost-dir'
EVENT_ENGINE_INCLUDE_CMD = '--event-engine-include'
EVENT_ENGINE_LIB_CMD = '--event-engine-lib'

#sys.setdefaultencoding("UTF-8")

#module1 = Extension('keystone',
#		include_dirs = [
#		'/Users/RK/Desktop/shared_folder/project/keystone-strategy-engine/lib/boost_1.58_mac/include',
#		'/Users/RK/Desktop/shared_folder/project/keystone-strategy-engine/src/'],
#		libraries = ['boost_system', 'boost_thread', 'eventengine'],
#		library_dirs = [
#		'/Users/RK/Desktop/shared_folder/project/keystone-strategy-engine/lib/boost_1.58_mac/lib',
#		'/Users/RK/Desktop/shared_folder/project/keystone-strategy-engine/lib/mac/'],
#		extra_compile_args = ['-std=c++0x','-stdlib=libc++','-mmacosx-version-min=10.7'],
#		extra_link_args = ['-stdlib=libc++','-mmacosx-version-min=10.7'],
#		language = 'c++',
#		sources = ['kspython_interface.cpp'])

# module1 = Extension('keystone',
# 		include_dirs = [
# 		'/mnt/hgfs/project/keystone-strategy-engine/lib/boost_1.58_unix/include',
# 		'/mnt/hgfs/project/keystone-strategy-engine/src/'],
# 		libraries = ['eventengine', 'boost_system', 'boost_thread'],
# 		library_dirs = [
# 		'/mnt/hgfs/project/keystone-strategy-engine/lib/boost_1.58_unix/lib',
# 		'/mnt/hgfs/project/keystone-strategy-engine/lib/unix/'],
# 		extra_compile_args = ['-std=c++0x'],
# 		language = 'c++',
# 		sources = ['kspython_interface.cpp'])

#http://victorjabur.com/2011/06/05/compiling-python-2-7-modules-on-windows-32-and-64-using-msvc-2008-express/
def parse_option(arg, name):
    if arg.find(name) == 0:
        idx = arg.find(name + '=')
        if idx == -1:
            raise TypeError('Unknow option ' + arg)
        else:
            return arg[len(name)+1:].strip()
    else:
        return None

if __name__ == '__main__':
    args = copy.copy(sys.argv)
    for arg in args:
        # parse boost dir
        ret = parse_option(arg, BOOST_HOME_CMD)
        if ret is not None:
            BOOST_HOME = ret
            sys.argv.remove(arg)
            continue
        # parse event engine include
        ret = parse_option(arg, EVENT_ENGINE_INCLUDE_CMD)
        if ret is not None:
            EVENT_ENGINE_INCLUDE = ret
            sys.argv.remove(arg)
            continue
        # parse event engine include
        ret = parse_option(arg, EVENT_ENGINE_LIB_CMD)
        if ret is not None:
            EVENT_ENGINE_LIB = ret
            sys.argv.remove(arg)
            continue

    print("BOOST_HOME: " + BOOST_HOME)
    print("EVENT_ENGINE_INCLUDE: " + EVENT_ENGINE_INCLUDE)
    print("EVENT_ENGINE_LIB: " + EVENT_ENGINE_LIB)

    # compile and link args
    libraries = ['boost_system', 'boost_thread', 'eventengine']
    extra_compile_args = []
    extra_link_args = []
    if _platform == "linux" or _platform == "linux2":
       # linux
       extra_compile_args = ['-std=c++0x']
       extra_link_args =[]
    elif _platform == "darwin":
       # MAC OS X
       extra_compile_args = ['-std=c++0x','-stdlib=libc++','-Wno-unused-local-typedefs']
       extra_link_args = ['-stdlib=libc++']
    elif _platform == "win32":
       # Windows
       extra_compile_args = ['/EHsc']
       extra_link_args =[]
       libraries = ['eventengine']

    # c++ extension
    module1 = Extension('keystone.engine',
    		include_dirs = [
    		'./keystone/engine/',
    		BOOST_HOME + '/include',
            EVENT_ENGINE_INCLUDE],
    		libraries = libraries,
    		library_dirs = [
    		BOOST_HOME + '/lib',
    		EVENT_ENGINE_LIB],
    		extra_compile_args = extra_compile_args,
            extra_link_args = extra_link_args,
    		language = 'c++',
    		sources = ['./keystone/engine/kspython_interface.cpp'])

    # setup
    setup (name = 'keystone_sdk',
    		version = '0.0.1',
    		description = 'keystone python SDK for backtesting',
            packages=find_packages('.', include=['keystone', 'keystone.*']),
    		ext_modules = [module1])
