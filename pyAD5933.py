import smbus
from math import atan, sqrt
from time import sleep
import csv
from datetime import datetime

#Function for log file name
def f_name():
	i = datetime.now()
	file_name = "log-" + ("%s_%s_%s-%s_%s" %(i.day, i.month, i.year, i.hour, i.minute)) + ".csv"
	return file_name

# Conversion functions
def magnitude(real, img):
    return sqrt(real * real + img * img)

def phase(real, img):
    return atan(img / real)

# Help functions to work at the bit level
def set_bit(n, reg):
	return reg | (1 << n)

def clear_bit(n, reg):
	return reg & (0xFF & 0 << n)

# List of all the registers
CONTROL_REG0 = 			0x80
CONTROL_REG1 = 			0x81

FREQ_MIN_REG0 = 		0x82
FREQ_MIN_REG1 = 		0x83
FREQ_MIN_REG2 = 		0x84

FREQ_INC_REG0 = 		0x85
FREQ_INC_REG1 = 		0x86
FREQ_INC_REG2 = 		0x87

INC_NUM_REG0 = 			0x88
INC_NUM_REG1 = 			0x89

STTL_TIME_CY_NUM_REG0 = 0x8A
STTL_TIME_CY_NUM_REG1 = 0x8B

STATUS_REG = 			0x8F

TEMP_DATA_REG0 = 		0x92
TEMP_DATA_REG1 = 		0x93

REAL_DATA_REG0 = 		0x94
REAL_DATA_REG1 = 		0x95

IMG_DATA_REG0 = 		0x96
IMG_DATA_REG1 = 		0x97

MAX_FREQ = 				100e3
MIN_FREQ = 				1e3

# Device address
ADDR_DEV = 0x60  ######################## find the right address

# AD5933 commands
INIT_WITH_START_FREQ = 	(0x01 << 4)
START_FREQ_SWEEP = 		(0x02 << 4)
INCREMENT_FREQ = 		(0x03 << 3)
REPEAT_FREQ = 			(0x04 << 4)
MEASURE_TEMP = 			(0x09 << 4)
POWER_DOWN = 			(0x0A << 4)
STANDBY = 				(0x0B << 4)
RESET = 				(0x01 << 4)
IDLE = 					(0x00 << 4)

# Voltage indexes
V_OUT_1 = 				1
V_OUT_2 = 				2
V_OUT_04 = 				3
V_OUT_02 = 				4

class AD5933:
    def __init__(self, clk):
        self.bus = smbus.SMBus(0)
        self.control_reg_value0 = 0x00
        self.control_reg_value1 = 0x00
        self.clk = clk
        self.set_clock(self.clk)
    
    def calibrate(self):


    def init(self):
		# used to init the AD5933
		self.set_ex_voltage(2)
		self.set_PGA_gain(1)
		self.set_settling_time(511)

    # Measurement methodes
    def make_imp_measure(self, min_freq, num_inc, freq_inc):
    	current_freq = min_freq
    	current_img = 0
    	current_real = 0
		self.set_freq_range(min_freq, num_inc, freq_inc)
		self.send_cmd(STANDBY)
		self.send_cmd(INIT_WITH_START_FREQ)
		sleep(0.1)  # Wait for the settling time
		self.send_cmd(START_FREQ_SWEEP)
		with open(f_name(), 'wt') as csvfile:
			spamwriter = csv.writer(csvfile, delimiter=';')
			spamwriter.writerow(['Freq', 'Real', 'Img'])
			while not self.is_sweep_complete():
				while not self.is_meas_imp_complete():
					pass
				current_img = self.read_img_reg()
				current_real = self.read_real_reg()
				spamwriter.writerow([str(current_freq), str(current_real), str(current_img)])
				self.send_cmd(INCREMENT_FREQ)
				current_freq += freq_inc
		self.send_cmd(POWER_DOWN)

    def make_temp_measure(self):
		self.send_cmd(MEASURE_TEMP)
		while not self.is_meas_temp_complete():
			pass
		temp = (self.read_reg(TEMP_DATA_REG0) << 8) | self.read_reg(TEMP_DATA_REG1)
		if temp < 8192:
			temp = temp / 32
		else:
			temp = temp - 16384
			temp = temp / 32
		return temp

    def set_clock(self):
        if self.clk >= 16.667:
            self.control_reg_value1 = 0b11110111 & self.control_reg_value1
            self.write_reg(CONTROL_REG1, self.control_reg_value1)
            print "MCLK set to internal clock."
        else:
            self.control_reg_value1 = 0b00001000 | self.control_reg_value1
            self.write_reg(CONTROL_REG1, self.control_reg_value1)
            print "MCLK set to {} Hz".format(self.clk)

    # Methods to edit control register
    def set_freq_range(self, min=1e3, inc=500, freq_inc=198):
    	"""
        Set the frequency sweep parameters
        
        Keyword arguments:
        min -- start frequency
        inc -- number of incrments
        freq_inc -- frequency incrment
    	"""
        if min <= MIN_FREQ or min > MAX_FREQ or (inc * freq_inc) > MAX_FREQ:
            try:
            	raise NameError("Frequencies not in the range")
            except NameError:
            	print "A problem has occured when setting the sweep frequencies."
            	print "Please, controle the frequencies you entered."
            	raise e

        min = int((min / (self.clk / 4)) * pow(2, 27))
        freq_inc = int((freq_inc / (self.clk / 4)) * pow(2, 27))

        self.write_reg(FREQ_MIN_REG2, (min >> 16) & 0x00FF)
        self.write_reg(FREQ_MIN_REG1, (min >> 8 ) & 0x00FF)
        self.write_reg(FREQ_MIN_REG0, min & 0x00FF)

        self.write_reg(FREQ_INC_REG2, (freq_inc >> 16) & 0x00FF)
        self.write_reg(FREQ_INC_REG1, (freq_inc >> 8 ) & 0x00FF)
        self.write_reg(FREQ_INC_REG1, freq_inc & 0x00FF)

        self.write_reg(INC_NUM_REG0, inc >> 8)
        self.write_reg(INC_NUM_REG1, inc & 0xFF)

    def set_PGA_gain(self, gain=1):
    	if gain == 1:
    		self.control_reg_value0 = self.control_reg_value0 | 1
    	else:
    		self.control_reg_value0 = self.control_reg_value0 & 0xFE
		self.write_reg(CONTROL_REG0, self.control_reg_value0)

    def set_ex_voltage(self, voltage=2):
		if voltage == 4:  # for 200mV
			self.control_reg_value0 = set_bit(3, self.control_reg_value0)
			self.control_reg_value0 = clear_bit(4, self.control_reg_value0)
		elif voltage == 3:  # for 400mV
			self.control_reg_value0 = set_bit(4, self.control_reg_value0)
			self.control_reg_value0 = clear_bit(3, self.control_reg_value0)
		elif voltage == 2:  # for 2V
			self.control_reg_value0 = set_bit(3, self.control_reg_value0)
			self.control_reg_value0 = set_bit(4, self.control_reg_value0)
		elif voltage == 1:  # for 1V
			self.control_reg_value0 = clear_bit(3, self.control_reg_value0)
			self.control_reg_value0 = clear_bit(4, self.control_reg_value0)
		self.write_reg(CONTROL_REG0, self.control_reg_value0)

    def set_settling_time(self, cy_num, factor=1):
		if cy_num > 511 or cy_num < 0 or factor != 1 or factor != 2 or factor != 4:
			return False
		if factor == 1:
			if cy_num >= 256:
				self.write_reg(STTL_TIME_CY_NUM_REG0, 0b00000001)
			else:
				self.write_reg(STTL_TIME_CY_NUM_REG0, 0b00000000)
			self.write_reg(STTL_TIME_CY_NUM_REG1, cy_num / 2)
		if factor == 2:
			if cy_num >= 256:
				self.write_reg(STTL_TIME_CY_NUM_REG0, 0b00000011)
			else:
				self.write_reg(STTL_TIME_CY_NUM_REG0, 0b00000010)
			self.write_reg(STTL_TIME_CY_NUM_REG1, cy_num / 2)
		elif factor == 4:
			if cy_num >= 256:
				self.write_reg(STTL_TIME_CY_NUM_REG0, 0b00000111)
			else:
				self.write_reg(STTL_TIME_CY_NUM_REG0, 0b00000110)
		    self.write_reg(STTL_TIME_CY_NUM_REG1, cy_num / 2)

    def is_meas_imp_complete(self):
        status = self.read_reg(STATUS_REG)
        if (status & 0x01) == 1:
            return True
        else:
            return False

    def is_meas_temp_complete(self):
        status = self.read_reg(STATUS_REG)
        if (status & 0x02) == 2:
            return True
        else:
            return False

    def is_sweep_complete(self):
        status = self.read_reg(STATUS_REG)
        if (status & 0x04) == 4:
            return True
        else:
            return False

	def send_cmd(cmd):
		if cmd == INIT_WITH_START_FREQ:
			self.control_reg_value0 |= INIT_WITH_START_FREQ
			self.write_reg(CONTROL_REG0, self.control_reg_value0)
		elif cmd == START_FREQ_SWEEP:
			self.control_reg_value0 |= START_FREQ_SWEEP
			self.write_reg(CONTROL_REG0, self.control_reg_value0)
		elif cmd == INCREMENT_FREQ:
			self.control_reg_value0 |= INCREMENT_FREQ
			self.write_reg(CONTROL_REG0, self.control_reg_value0)
		elif cmd == REPEAT_FREQ:
			self.control_reg_value0 |= REPEAT_FREQ
			self.write_reg(CONTROL_REG0, self.control_reg_value0)
		elif cmd == MEASURE_TEMP:
			self.control_reg_value0 |= MEASURE_TEMP
			self.write_reg(CONTROL_REG0, self.control_reg_value0)
		elif cmd == POWER_DOWN:
			self.control_reg_value0 |= POWER_DOWN
			self.write_reg(CONTROL_REG0, self.control_reg_value0)
		elif cmd == STANDBY:
			self.control_reg_value0 |= STANDBY
			self.write_reg(CONTROL_REG0, self.control_reg_value0)
		elif cmd == RESET:
			self.control_reg_value1 |= RESET
			self.write_reg(CONTROL_REG1, self.control_reg_value1)
		elif cmd == IDLE:
			self.control_reg_value0 |= IDLE
			self.write_reg(CONTROL_REG0, self.control_reg_value0)
		else:
			return False

	def read_img_reg():
		return (self.read_reg(IMG_DATA_REG0) << 8) | self.read_reg(IMG_DATA_REG1)

	def read_real_reg():
		return (self.read_reg(REAL_DATA_REG0) << 8) | self.read_reg(REAL_DATA_REG1)

    # Low level methods
    def read_reg(self, reg):
        self.bus.read_byte_data(ADDR_DEV, reg)

    def write_reg(self, reg, value):
        self.bus.write_byte_data(ADDR_DEV, reg, value)