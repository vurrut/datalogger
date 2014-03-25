import time
import smbus
import logging
from array import array

CMD_CHECK_VERSION = 0xe0
CMD_INIT_MODBUS_SLAVE = 0xe1
CMD_REQUEST_MODBUS_SENSOR = 0xe2
LATENCY = 0.001

class MCUModbusSlaveReader:
    def __init__(self, bus_nr, mcu_address):
        self.logger = logging.getLogger(__name__)
        self.bus = smbus.SMBus(int(bus_nr))
        self.mcu_address = int(mcu_address)
    
    def check_mcu_connection(self):
        try:
            char = array('B', [0, 0, 0])
            self.bus.write_byte(self.mcu_address, CMD_CHECK_VERSION)
            time.sleep(LATENCY)
            char[0] = self.bus.read_byte(self.mcu_address)
            self.bus.write_byte(self.mcu_address, CMD_CHECK_VERSION)
            time.sleep(LATENCY)
            char[1] = self.bus.read_byte(self.mcu_address)
            self.bus.write_byte(self.mcu_address, CMD_CHECK_VERSION)
            time.sleep(LATENCY)
            char[2] = self.bus.read_byte(self.mcu_address)
        except Exception as e:
            self.logger.error("Couldn't connect with mcu")
            return False
        return True

    def request_modbus_value(self, modbus_address, register_address):
        try:
            self.bus.write_byte(self.mcu_address, CMD_INIT_MODBUS_SLAVE)
            self.bus.write_byte(self.mcu_address, modbus_address)
            self.bus.write_byte(self.mcu_address, register_address)
            time.sleep(.1)
            self.logger.debug('Address %s and register %s set to read',
                              modbus_address, register_address)
        except Exception as e:
            self.logger.error("Connection with mcu lost")
            return False
        return True

    def read_16bit_value(self):
        char = array('B', [0, 0])
        self.bus.write_byte(self.mcu_address, CMD_REQUEST_MODBUS_SENSOR)
        
        while char[0] == 0:
            time.sleep(LATENCY)
            char[0] = self.bus.read_byte(self.mcu_address)
        
        if char[0] == 255:
            time.sleep(LATENCY)
            char[0] = self.bus.read_byte(self.mcu_address)
            time.sleep(LATENCY)
            char[1] = self.bus.read_byte(self.mcu_address)
        
        self.logger.debug('16bit value read from mcu: ' + char)
        return char

    def read_8bit_value(self):
        char = array('B', [0, 0])
        self.bus.write_byte(self.mcu_address, CMD_REQUEST_MODBUS_SENSOR)
        
        while char[0] == 0:
            time.sleep(LATENCY)
            char[0] = self.bus.read_byte(self.mcu_address)
        
        if char[0] == 255:
            time.sleep(LATENCY)
            char[0] = self.bus.read_byte(self.mcu_address)
        self.logger.debug('8bit value read from mcu: ' + char)
        return char
