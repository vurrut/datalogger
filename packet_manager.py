from apscheduler.scheduler import Scheduler
from datetime import timedelta, time, datetime, date
import configuration
from connection_manager import ConnectionManager
from configuration_manager import ConfigurationManager
import time
import logging
import json

RETRY_SEND_PACKETS_INTERVAL = 20

class PacketManager():
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.packets = []
        self.logger = logging.getLogger(__name__)
        self.update_configuration()
       
    def update_configuration(self):
        try:
            self.checksum = configuration.get_checksum()
            self.packet_send_interval = configuration.get_time_interval_to_send_packets()
            self.minimum_packets_to_send = configuration.get_minimum_packets_to_send()
        except:
            self.logger.warning('Failed to update configuration of %s' % __name__)   
    
    def initiate_send_packets(self, connection):
        self.connection = connection
        self.update_configuration()
        
        try:
            self.scheduler.unschedule_func(self.send_packets_job)
        except:
            pass
       
        try:
            #start job to send packets
            self.scheduler.add_interval_job(self.send_packets_job,
                                            seconds=self.packet_send_interval)
        except:
            self.logger.error("Failed to start send packets job, incomplete configuration")

    def send_packets_job(self):
        if self.minimum_packets_to_send < len(self.packets):
            #try to send packets
            nr_of_sent_packets = self.connection.send_packets(self.packets)
            if nr_of_sent_packets > 0: 
                #success, clear sent packets
                del self.packets[0:nr_of_sent_packets]
        else:
            #not enough packets to send, initiate job with small interval to keep checking
            #number of packets
            try:
                self.scheduler.unschedule_func(self.check_packets_to_send)
            except:
                pass

            self.scheduler.add_interval_job(self.check_packets_to_send,
                                            seconds=RETRY_SEND_PACKETS_INTERVAL)

    def check_packets_to_send(self):
         if self.minimum_packets_to_send < len(self.packets):
            #stop this timer
            try:
                self.scheduler.unschedule_func(self.check_packets_to_send)
            except:
                pass
            #try to send packets
            self.send_packets_job()

    def store_packet_in_memory(self, type, values):
        #type, timestamp, values
        timestamp = time.mktime(datetime.now().timetuple())
        packet = {'checksum': self.checksum, 'type': type, 'timeDate': timestamp, 'sensorData': values}
        self.packets.append(packet)

    def remove_all_packets_from_memory(self):
        self.packets = []
