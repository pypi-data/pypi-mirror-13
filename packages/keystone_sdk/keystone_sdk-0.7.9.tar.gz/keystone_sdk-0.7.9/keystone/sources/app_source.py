# -*- coding: utf-8 -*-

from __future__ import print_function
import json
import abc
import pandas as pd
from datetime import datetime
from six import with_metaclass

class AppUniverse(object):
	def __init__(self, path):
		self.path = path
		self.
class KSDataEvent(object):
	data = []
	def __init__(self, path):
		pass

	@classmethod
	def addSource(cls, path, config):