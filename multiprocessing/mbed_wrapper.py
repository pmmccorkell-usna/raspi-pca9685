import mbed
from time import sleep
from json import dumps,loads
# from multiprocessing import Process, Pipe


class BNO:
	def __init__(self,communicator):
		self.comms=communicator
		self.run=1
	
	def stream(self):
		while(self.run):
			self.data=mbed.get_angles()
			# print('mbed.py: '+dumps(self.data))
			self.comms.send(self.data)
			sleep(0.01)

	def close(self):
		self.run = 0