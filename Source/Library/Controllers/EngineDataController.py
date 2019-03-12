# ||=======================================================================||
# ||
# ||  Program/File:		EngineDataController.py
# ||
# ||  Description:		Singleton To Represent Current Data Model
# ||
# ||  Author:           Logan Wilkovich
# ||  Email:            LWilkovich@gmail.com
# ||  Creation Date:	24 December 2018 | Logan Wilkovich
# ||=======================================================================||
# ||=======================||
# Library
from ConfigLoader import ConfigLoader
from DebugLogger import DebugLogger
# Data
from NetworkClientCache import NetworkClientCache
# Premades
from time import sleep, time, strftime, localtime
from threading import Thread
import traceback
import ast
# ||=======================||
# Global Variables

# ||=======================||
# Notes

# ||=======================||
# ||=======================================================================||

class EngineDataController(object):

	def __init__(self):
		self.type = "EngineDataController"

		self.active = False

		# ||=======================||
		# Data Storage Types
		self.networkClientCache = NetworkClientCache()
		
		# ||=======================||
		# Program Classes
		configLoader = ConfigLoader()
		self.config = configLoader.getConfig(self.type)

		self.debugLogger = DebugLogger(self.type)
		self.debugLogger.setMessageSettings(
			ast.literal_eval(self.config["Debug"]),
			ast.literal_eval(self.config["Standard"]),
			ast.literal_eval(self.config["Warning"]),
			ast.literal_eval(self.config["Error"]))

		# ||=======================||
		# Communication Pipes
		self.networkClientPipe = None

		# ||=======================||
		# Config <bool>
		self.debug = self.config["Debug"]
		self.log = self.config["Log"]
		self.useCache = {
			"NetworkClient": self.config["useNetworkClientCache"]
		}

		# ||=======================||
		# Defaults
		self.duty = "Inactive"
		self.parentPipes = []
		self.childPipes = []

# ||=======================================================================||

	def updateCurrentDuty(self, duty):
		self.duty = duty

# ||=======================================================================||

	def jsonify(self, message = "Null", time = strftime("%a;%d-%m-%Y;%H:%M:%S", localtime()), function = "jsonify"):
		return {
			"Generic Information": {
				"_Class": self.type,
				"_Function": function,
				"Duty": self.duty,
				"Return Status": True,
				"Activity": self.active,
				"Message": message,
				"Time": time
			},
			"Specific Information": {
				"Debug": self.debug
			}
		}
		
# ||=======================================================================||

	def pushChildPipe(self, _class, pipe):
		self.childPipes.append((_class, pipe))

# ||=======================================================================||

	def pipeCommand(self, command, pipe):
		pipe.send(command)
		returnData = "Empty"
		for i in range(10):
			if (pipe.poll(0.5)):
				returnData = pipe.recv()
				return returnData
		if (returnData == "Empty"):
			logMessage = "Failed To Recieve Data From The networkClientPipe"
			self.debugLogger.log("Error", self.type, logMessage)
	
			returnData = None
			return returnData

# ||=======================================================================||

	def pushParentPipe(self, pipe):
		self.parentPipes.append(pipe)	

# ||=======================================================================||

	def communicationModule(self):
		while (1):
			if (len(self.parentPipes) != 0):
				dataRecv = None
				while (dataRecv == None):
					for i in range(len(self.parentPipes)):
						pipe = self.parentPipes[i]
						# print("Pipe:",i)
						try:
							if (pipe.poll(0.5)):
								dataRecv = pipe.recv() * 3
						except Exception as e:
							print(e)
				# print(dataRecv)

				logMessage = "Reading From Pipe"
				self.debugLogger.log("Debug", self.type, logMessage)

				interactionAccess = {
					"NetworkClient.getLiveData": partial(self.networkClientCache.getLiveData),
					"NetworkClient.setLiveData": partial(self.networkClientCache.setLiveData, dataRecv[1]),
					"NetworkClient.getInternalLog": partial(self.networkClientCache.getInternalLog, dataRecv[1]),
					"NetworkClient.pushInternalLog": partial(self.networkClientCache.pushInternalLog, dataRecv[1])
				}
				denyCode = False
				if (dataRecv[0].find("NetworkClientCache") != -1):
					if (self.useNetworkClientCache == False):
						denyCode = True

				if (denyCode == True):
					logMessage = "Pipe Command Denied: " + str(dataRecv)
					self.debugLogger.log("Error", self.type, logMessage)
					comPipe.send("Denied")
					return 0
				else:
					returnData = interactionAccess[dataRecv[0]]()

					logMessage = "Executing Pipe Command: " + str(dataRecv)
					self.debugLogger.log("Debug", self.type, logMessage)

					comPipe.send(returnData)
					return 0
				return 0

# ||=======================================================================||

	def syncEngineData(self):
		while (1):
			for i in range(len(self.childPipes)):
				curPipe = self.childPipes[i]
				if (self.useCache[curPipe[0]]):
					command = ["jsonify"]
					currentData = self.pipeCommand(command, curPipe[1])
					self.networkClientCache.setLiveData(currentData)

					logMessage = curPipe[0] + " Data Successfully Synced"
					self.debugLogger.log("Standard", self.type, logMessage)

			sleep(1)

			logMessage = "Engine Data Successfully Synced"
			self.debugLogger.log("Debug", self.type, logMessage)

# ||=======================================================================||