# -*- coding: utf-8 -*-

from __future__ import print_function
import json
import abc
import pandas as pd
from datetime import datetime
from six import with_metaclass

DATAFRAME_KEY = "dataframe"

class KSTableFile(object):
	def __init__(self, path):
		self.path = path

	def readDataframe(self, key=DATAFRAME_KEY):
		return pd.read_hdf(self.path, key)

	def writeDataframe(self, dataframe, key=DATAFRAME_KEY, mode='w'):
		if not isinstance(dataframe, pd.DataFrame):
			raise TypeError("KSTableFile::write_dataframe(): dataframe MUST be an instance of DataFrame")
		dataframe.to_hdf(self.path, key, mode=mode)