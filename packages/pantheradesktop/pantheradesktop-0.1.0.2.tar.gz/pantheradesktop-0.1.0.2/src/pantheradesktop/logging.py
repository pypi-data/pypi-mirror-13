#-*- encoding: utf-8 -*-

import inspect
from time import strftime, localtime
import time
import sys
import traceback

__author__ = "Damian Kęska"
__license__ = "LGPLv3"
__maintainer__ = "Damian Kęska"
__copyright__ = "Copyleft by Panthera Desktop Team"

class pantheraLogging:
    """
        Simple logging and debugging class for Panthera Desktop Framework
        
    """

    logging = True
    silent = False
    session = ""
    panthera = ""
    lastLogTime = 0
    lastMsgTime = 0
    dateFormat = 'number'
    
    
    
    def initializeTimer(self):
        """
            Initialize timer for benchmarking custom code blocks
        """
    
        self.lastLogTime = time.time()
    
    
    
    def convertMessage(self, message, stackPosition):
        """
            Format a message
            
            message - message
            stackPosition - function name on stack
            
            Returns string
        """
    
        diff = "-"
    
        if self.lastLogTime > 0:
            diff = str(time.time()-self.lastLogTime)+ " real"
        elif self.lastMsgTime > 0:
            diff = str(time.time()-self.lastMsgTime)
            
        self.lastMsgTime = time.time()
        diff = diff[0:10]

        timeStr = str(time.time())

        if self.dateFormat != 'number':
            timeStr = time.strftime(self.dateFormat, time.localtime(int(float(timeStr))))

        return "["+timeStr+", "+str(diff)+"] "+stackPosition+": "+message
        
        
    
    def __init__ (self, panthera, quiet=False):
        """ 
            Constructor, takes panthera object as argument 
        """
    
        self.panthera = panthera
        
        if quiet:
            self.silent = True
        
    def outputException(self, *args, **kwargs):
        self.output(*args, **kwargs)
        traceback.print_exc(file=sys.stdout)

    def output(self, message, group='', savetoLogs=True, execHook=True, skipDate=False):
        """ 
            Outputs to log file and to console 
        """
        
        if self.logging == False:
            return False
            
        if not skipDate:
            message = self.convertMessage(message, inspect.stack()[1][3])
            
        if self.silent == False:
            print(message)
            
        self.session += message + "\n"

    def flushAndEnablePrinting(self, clearSession=False):
        """
        Flush buffers and re-enable log printint to screen
        :param clearSession:
        :return:
        """

        print(self.session[0:-1])

        if clearSession:
            self.session = ""

        self.silent = False
