# -*- coding: utf-8 -*-

from __future__ import print_function
import json
import abc
import pandas as pd
from datetime import datetime
from six import with_metaclass

from keystone.sources.kstable import KSTableFile

# Universe file name
SECURITY_TABLE_FILE = "security.kstable"
SIGNAL_TABLE_FILE = "signal.kstable"
METADATA_FILE = "metadata"

# 
UNIVERSE_BASKET = "basket"
UNIVERSE_SID = "sids"

# Column name
DATETIME_COLUMN = "datetime"
SID_COLUMN = "sid"
PRICE_COLUMN = "price"

class AppUniverse(object):
	def __init__(self, path):
		self.path = path
		self._securityDataFile = path + '/' + SECURITY_TABLE_FILE
		self._signalDataFile = path + '/' + SIGNAL_TABLE_FILE
		self._metaDataFile = path + '/' + METADATA_FILE

		self.basket = []
		self.sids = []
		if not self._check():
			raise ValueError(path + " is not a App Universe Data")
		self._loadMetadata()

	def _check(self):
		return True

	def _loadMetadata(self):
		metadata = json.load(file(self._metaDataFile))
		self.basket = metadata[UNIVERSE_BASKET]
		self.sids = metadata[UNIVERSE_SID]

	def readSecurityDataFrame(self):
		f = KSTableFile(self._securityDataFile)
		return f.readDataframe()

	def readSignalDataFrame(self):
		f = KSTableFile(self._signalDataFile)
		return f.readDataframe()

class KSDataEvent(object):
	securityData = []
	signalData = []
	appUniverse = []
	def __init__(self):
		pass

	@classmethod
	def addSource(cls, path, config):
		'''
		config: List of basket name
		'''
		uni = AppUniverse(path)
		cls.appUniverse.append(uni)
		for basketName in config and basketName in uni.basket:
			sids = uni.basket[basketName]
			# filter dataframe
			df = uni.readSecurityDataFrame()
			df = df[df[SID_COLUMN].isin(sids)]
			cls.data.append(df)

	@classmethod
			
