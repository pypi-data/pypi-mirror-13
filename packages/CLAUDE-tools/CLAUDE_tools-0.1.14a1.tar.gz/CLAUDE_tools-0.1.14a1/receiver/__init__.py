'''
Created on Sep 10, 2015

@author: andrei
'''
from abc import ABCMeta, abstractmethod
import logging

import tools.messaging as messaging
import tools.auxiliary as auxiliary

class MessageReceiver(object):
    '''
    classdocs
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def callback(self, message):
        pass
    
    def run(self):
        consumer = messaging.MessageConsumer(
                                                    messaging.buildRabbitMQConnectionLink(),
                                                    self.queue,
                                                    self.callback,
                                                    )
        consumer.constantConsuming()
        
    def init(self, log_file, queue, log_lvl = logging.DEBUG):
        self.logger = auxiliary.initLogger(log_file, log_lvl)
        self.queue = queue
    
    def __init__(self):
        pass