#-*- encoding: utf-8 -*-

import inspect
import time
import traceback

__author__ = "Damian Kęska"
__license__ = "LGPLv3"
__maintainer__ = "Damian Kęska"
__copyright__ = "Copyleft by Panthera Desktop Team"

class pantheraHooking:
    """
        Hooking (plugins support) module for Panthera Desktop Framework

    """

    hooksList = {}
    
    def addOption(self, hookName, func, priority=99):
        """
            Connect method to a hooking slot
            
            hookName - hooking slot name
            func - function address
            priority - 0-99 priority number (lowest = higher priority)
            
            Returns bool
        """
        
        if priority > 99 or priority < 0:
            raise Exception('Priority should be in range of 0 to 99')
            return False

        # create array if there is no any hooked function yet
        if not hookName in self.hooksList:
            self.hooksList[hookName] = {}

        argsData = False

        try:
            args = inspect.getargspec(func).args

            if (len(args) > 0 and args[0] != 'self') or (len(args) > 1 and args[0] == 'self'):
                argsData = True

        except Exception:
            pass
            
        self.hooksList[hookName][str(priority)+'_'+str(func.__str__)] = {
            'callback': func,
            'argsData': argsData,
            'priority': priority,
            'created': time.time(),
            'executed': 0
        }
        
        return True


    def removeAllByClass(self, objectClassName):
        """
        Remove all hooks that reffers to selected object type
        :param objectClassName:
        :return: int Number of affected hooks
        """

        i = 0

        for hookName, hooks in self.hooksList.iterkeys():
            for id, hook in hooks.iterkeys():
                if hasattr(hook['callback'], 'im_class') and hook['callback'].im_class.__name__ == objectClassName:
                    self.removeOption(hook['callback'], hookName)
                    i = i + 1

        return i

        
    def execute(self, hookName, data=''):
        """
            Execute all functions on selected slot
            
            hookName - hooking slot name
            data - data to pass
            
            Returns data
        """
    
        if not hookName in self.hooksList:
            return data

        for func in sorted(self.hooksList[hookName]):
            try:
                # get data

                if self.hooksList[hookName][func]['argsData']:
                    data = self.hooksList[hookName][func]['callback'](data)
                else:
                    data = self.hooksList[hookName][func]['callback']()

                # increase counter
                self.hooksList[hookName][func]['executed'] = self.hooksList[hookName][func]['executed'] + 1
            except Exception as e:
                print('Hook: '+hookName)
                print('Data: '+str(data))
                #raise RuntimeError('Cannot execute hooked function: "'+str(self.hooksList[hookName][func]['callback'])+'" in "'+hookName+'" slot, error details: '+str(e), 1)
                traceback.print_exc()
            
        return data


    def hookExists(self, hookName):
        """
            Check if hooking slot exists
            
            hookName - hooking slot name
            
            Returns bool
        """

        return hookName in self.hooksList


    def removeOption(self, func, hookName=None):
        """
            Remove an option from hooking slot
            
            func - function
            hookName - hooking slot name
            
            Returns bool
        """
    
        return isConnected(func, hookName, True)


    def isConnected(self, func, hookName=None, removeHook=False):
    
        """
            Check if selected function is connected to selected or any hook slot
            
            func - function
            hookName - optional hooking slot
            
            Returns bool
        """
        
        for name in self.hooksList:
        
            if hookName is not None:
                if not self.hookExists(hookName):
                    return False
            
                name = self.hooksList[hookName]
        
            for hook in name:
                if hook['callback'] == func:
                    if removeHook:
                        del self.hooksList[hookName]
                
                    return True
    
            if hookName is not None:
                return False
