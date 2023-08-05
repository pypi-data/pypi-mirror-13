'''
Created on Oct 1, 2015

@author: andrei
'''

class Error(Exception):
    '''
    '''

    def __init__(self, msg, do_log=False):
        Exception.__init__(self, msg)
        
class ConfigurationError(Error):
    '''
    '''
    pass