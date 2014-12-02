import smbus
from math import atan, sqrt
from time import sleep

# Conversion functions
def magnitude(real, img):
    return sqrt(real*real + img*img)

def phase(real, img):
    return atan(img/real)

def set_bit(n, reg):
	return reg | (1 << n)

def clear_bit(n, reg):
	return reg & (0xFF & 0 << n)

CONTROL_REG0 = 0x80
CONTROL_REG1 = 0x81

FREQ_MIN_REG0 = 0x82
FREQ_MIN_REG1 = 0x83
FREQ_MIN_REG2 = 0x84

FREQ_INC_REG0 = 0x85
FREQ_INC_REG1 = 0x86
FREQ_INC_REG2 = 0x87

INC_NUM_REG0 = 0x88
INC_NUM_REG1 = 0x89

STTL_TIME_CY_NUM_REG0 = 0x8A
STTL_TIME_CY_NUM_REG1 = 0x8B

STATUS_REG = 0x8F

TEMP_DATA_REG0 = 0x92
TEMP_DATA_REG1 = 0x93

REAL_DATA_REG0 = 0x94
REAL_DATA_REG1 = 0x95

IMG_DATA_REG0 = 0x96
IMG_DATA_REG1 = 0x97

MAX_FREQ = 100e3
MIN_FREQ = 1e3

ADDR_DEV = 0x60 ######################## find the right address


class AD5933:
    def __init__(self, clk_source, clk=16.667e6):
        self.bus = smbus.SMBus(0)
        self.control_reg_value0 = 0x00
        self.control_reg_value1 = 0x08

        # Control register init
        self.write_reg(CONTROL_REG0, self.control_reg_value0)
        self.write_reg(CONTROL_REG1, self.control_reg_value1)

        if clk_source == "int":
            self.int_clk = True
        else:
            self.int_clk = False
        self.clk = clk

    # Measurement methodes
    def make_imp_measure(self):
    	set_freq_range(1000, 1000000, 500)
    	put_in_standby()
    	init_start_freq()


    def make_temp_measure(self):

    def set_mclk(self):
        if self.int_clk:
            self.control_reg_value1 = 0b11110111 & self.control_reg_value1
            self.write_reg(CONTROL_REG1, self.control_reg_value1)
        else:
            self.control_reg_value1 = 0b00001000 | self.control_reg_value1
            self.write_reg(CONTROL_REG1, self.control_reg_value1)

    # Methods to edit control register
    def set_freq_range(self, min, max, inc):
        if min <= 1000 or min >= max or min > 100e3:
            return False
        min_code = hex((min/(self.clk/4))*pow(2, 27))
        max_code = hex((max/(self.clk/4))*pow(2, 27))
        inc_code = hex((inc/(self.clk/4))*pow(2, 27))

        self.write_reg(FREQ_MIN_REG2, (min_code >> 16) & 0x00FF)
        self.write_reg(FREQ_MIN_REG1, (min_code >> 8 ) & 0x00FF)
        self.write_reg(FREQ_MIN_REG0, min_code & 0x00FF)

        self.write_reg(FREQ_MAX_REG2, (max_code >> 16) & 0x00FF)
        self.write_reg(FREQ_MAX_REG2, (max_code >> 8 ) & 0x00FF)
        self.write_reg(FREQ_MAX_REG2, max_code & 0x00FF)

        self.write_reg(FREQ_INC_REG2, (inc_code >> 16) & 0x00FF)
        self.write_reg(FREQ_INC_REG1, (inc_code >> 8 ) & 0x00FF)
        self.write_reg(FREQ_INC_REG1, inc_code & 0x00FF)

        return True

    def set_PGA_gain(self, gain=1):
    	control_reg_value1 = control_reg_value1 | 1
    	self.write_reg(CONTROL_REG1, control_reg_value1)

    def set_ex_voltage(self, voltage=2):
    	if voltage == 4:			# for 200mV
    		self.control_reg_value0 = set_bit(3, self.control_reg_value0)
    		self.control_reg_value0 = clear_bit(4, self.control_reg_value0)
    	elif voltage == 3:			# for 400mV
    		self.control_reg_value0 = set_bit(4, self.control_reg_value0)
    		self.control_reg_value0 = clear_bit(3, self.control_reg_value0)
    	elif voltage == 2:			# for 2V
    		self.control_reg_value0 = set_bit(3, self.control_reg_value0)
    		self.control_reg_value0 = set_bit(4, self.control_reg_value0)
    	elif voltage == 1:			# for 1V
    		self.control_reg_value0 = clear_bit(3, self.control_reg_value0)
    		self.control_reg_value0 = clear_bit(4, self.control_reg_value0)
    	write_reg(CONTROL_REG0, self.control_reg_value0)

    def set_settling_time(self, cy_num, factor):
    	if cy_num > 511 or cy_num < 0 or factor != 2 or factor != 4:
    		return False
    	if factor == 2:
    		if cy_num >= 256:
    			write_reg(STTL_TIME_CY_NUM_REG0, 0b00000011)
    		else:
    			write_reg(STTL_TIME_CY_NUM_REG0, 0b00000010)
    		write_reg(STTL_TIME_CY_NUM_REG1, cy_num / 2) 
    	elif factor == 4:
    		if cy_num >= 256:
    			write_reg(STTL_TIME_CY_NUM_REG0, 0b00000111)
    		else:
    			write_reg(STTL_TIME_CY_NUM_REG0, 0b00000110)
    		write_reg(STTL_TIME_CY_NUM_REG1, cy_num / 2) 


    def init_start_freq(self):
    	self.control_reg_value0 = clear_bit(15, self.control_reg_value0)
    	self.control_reg_value0 = clear_bit(14, self.control_reg_value0)
    	self.control_reg_value0 = clear_bit(13, self.control_reg_value0)
    	self.control_reg_value0 = set_bit(12, self.control_reg_value0)
    	write_reg(CONTROL_REG0, self.control_reg_value0)

    def start_freq_sweep(self):
    	self.control_reg_value0 = clear_bit(15, self.control_reg_value0)
    	self.control_reg_value0 = clear_bit(14, self.control_reg_value0)
    	self.control_reg_value0 = set_bit(13, self.control_reg_value0)
    	self.control_reg_value0 = clear_bit(12, self.control_reg_value0)
    	write_reg(CONTROL_REG0, self.control_reg_value0)


    def repeat_freq(self):
    	self.control_reg_value0 = clear_bit(15, self.control_reg_value0)
    	self.control_reg_value0 = set_bit(14, self.control_reg_value0)
    	self.control_reg_value0 = clear_bit(13, self.control_reg_value0)
    	self.control_reg_value0 = clear_bit(12, self.control_reg_value0)
    	write_reg(CONTROL_REG0, self.control_reg_value0)

    def incr_freq(self):
    	self.control_reg_value0 = clear_bit(15, self.control_reg_value0)
    	self.control_reg_value0 = clear_bit(14, self.control_reg_value0)
    	self.control_reg_value0 = set_bit(13, self.control_reg_value0)
    	self.control_reg_value0 = set_bit(12, self.control_reg_value0)
    	write_reg(CONTROL_REG0, self.control_reg_value0)

    def reset(self):
        self.control_reg_value1 = (1 << 4) | self.control_reg_value1
        self.write_reg(CONTROL_REG1, self.control_reg_value1)

    def put_in_standby(self):
        self.control_reg_value0 = ((0x0B << 4) | 0x0F) & self.control_reg_value0
        self.write_reg(CONTROL_REG0, self.control_reg_value0)

    def put_in_power_down(self):
        self.control_reg_value0 = ((0x0A << 4) | 0x0F) & self.control_reg_value0
        self.write_reg(CONTROL_REG0, self.control_reg_value0)

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

    # Low level methods
    def read_reg(self, reg):
        self.bus.read_byte_data(ADDR_DEV, reg)

    def write_reg(self, reg, value):
        self.bus.write_byte_data(ADDR_DEV, reg, value)