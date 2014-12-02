from pyAD5933 import *

class Measure:
	def __init__(self):
		#Initialize the AD5933 device
		self.device = AD5933("int")
		#Initialize place to manage measure array