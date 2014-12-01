import smbus
from math import atan, sqrt

# Conversion functions
def magnitude(real, img):
    return sqrt(real*real + img*img)

def phase(real, img):
    return atan(img/real)

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
            return -1
        min_code = hex((min/(self.clk/4))*pow(2, 27))
        max_code = hex((max/(self.clk/4))*pow(2, 27))





    def set_PGA_gain(self, gain=1):

    def set_clk_source(self, src):

    def set_ex_voltage(self, voltage=2):

    def start_freq_sweep(self):

    def repeat_freq(self):

    def incr_freq(self):


    def reset(self):
        self.control_reg_value1 = (1 << 4) | self.control_reg_value1
        self.write_reg(CONTROL_REG1, self.control_reg_value1)

    def standby(self):
        self.control_reg_value0 = ((0x0B << 4) | 0x0F) & self.control_reg_value0
        self.write_reg(CONTROL_REG0, self.control_reg_value0)

    def power_down(self):
        self.control_reg_value0 = ((0x0A << 4) | 0x0F) & self.control_reg_value0
        self.write_reg(CONTROL_REG0, self.control_reg_value0)

    def meas_imp_complete(self):
        status = self.read_reg(STATUS_REG)
        if (status & 0x01) == 1:
            return True
        else:
            return False

    def meas_temp_complete(self):
        status = self.read_reg(STATUS_REG)
        if (status & 0x02) == 2:
            return True
        else:
            return False

    def sweep_complete(self):
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