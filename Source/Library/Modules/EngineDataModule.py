# ||=======================================================================||
# ||
# ||  Program/File:		EngineDataModule.py
# ||
# ||  Description:		
# ||
# ||  Author:           Logan Wilkovich
# ||  Email:            LWilkovich@gmail.com
# ||  Creation Date:	11 March 2018 | Logan Wilkovich
# ||=======================================================================||
# ||=======================||
# Library
from ConfigLoader import ConfigLoader
from DebugLogger import DebugLogger
# Library/Controllers
from EngineDataController import EngineDataController
# Library/Cache
# Premades
from time import sleep, time, strftime, localtime
from threading import Thread
import traceback
import ast
import sys
import psutil
import os
# ||=======================||
# Global Variables
process = psutil.Process(os.getpid())
# ||=======================||
# Notes

# ||=======================||
# ||=======================================================================||

class EngineDataModule():
	def __init__(self):
		self.type = "EngineDataModule"

		# ||=======================||
		# Program Classes
		self.engineDataController = EngineDataController()

		# ||=======================||

		configLoader = ConfigLoader()
		self.config = configLoader.getConfig(self.type)

		# ||=======================||

		self.debugLogger = DebugLogger(self.type)
		self.debugLogger.setMessageSettings(
			ast.literal_eval(self.config["Debug"]),
			ast.literal_eval(self.config["Standard"]),
			ast.literal_eval(self.config["Warning"]),
			ast.literal_eval(self.config["Error"]))

# ||=======================================================================||

	def updateProcessMemorySize(self):
		self.processMemorySize = int(int(process.memory_info().rss) / 1000000)

# ||=======================================================================||

	def createProcess(self):
		logMessage = "Process Started"
		self.debugLogger.log("Standard", self.type, logMessage)

		# ||=======================||

		self.communicationThread = Thread(target = self.engineDataController.communicationModule)
		self.communicationThread.setDaemon(True)
		self.communicationThread.start()

		logMessage = "communicationThread Started"
		self.debugLogger.log("Standard", self.type, logMessage)
		
		# ||=======================||

		self.syncEngineDataThread = Thread(target = self.engineDataController.syncEngineData)
		self.syncEngineDataThread.setDaemon(True)
		self.syncEngineDataThread.start()

		logMessage = "syncEngineDataThread Started"
		self.debugLogger.log("Standard", self.type, logMessage)

		try:
			while(1):
				self.updateProcessMemorySize()
				logMessage = "Current Size In Megabytes: " + str(self.processMemorySize)
				self.debugLogger.log("Debug", self.type, logMessage)
				sleep(10)
		except KeyboardInterrupt as e:
			print('\r', end='')
			logMessage = "Process Joined"
			self.debugLogger.log("Standard", self.type, logMessage)
			return 0
		return 0

# ||=======================================================================||