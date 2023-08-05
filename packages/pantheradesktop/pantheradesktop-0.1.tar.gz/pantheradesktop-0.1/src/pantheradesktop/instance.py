#-*- encoding: utf-8 -*-
from pantheradesktop import pantheraClass
import os
import json
import copy
import sys
import subprocess

class pantheraJSONInstance(pantheraClass):
    pid = None

    def register(self, params=''):
        """
        Register instance of application to instances.json file so other instances or applications could know about runtime of this application
        :param params: Dictionary of parameters
        :hook panthera.instance.parameters: Dictionary of parameters
        :function self.registerParams: Dictionary of parameters
        :return: bool
        """

        instancesFile = self.app.filesDir+'/instances.json'

        ## if file does not exists then create an empty file
        if not os.path.isfile(instancesFile):
            w = open(instancesFile, 'w')
            w.write("{\n}")
            w.close()

        if type(params).__name__ is not "dict":
            params = dict()

        ## get self process id
        self.pid = str(os.getpid())

        params['process.user.login'] = os.getlogin()
        params['process.user.id'] = os.getuid()
        params['sys.argv'] = sys.argv

        ## add support for extensions
        if hasattr(self, 'registerParams'):
            params = self.registerParams(params)

        params = self.app.hooking.execute('panthera.instance.parameters', params)

        instancesList = json.loads(open(instancesFile).read())
        instancesList[self.pid] = params

        self.__writeToJSONFile(instancesList)
        return True

    def cleanup(self):
        """
        Clean up instances list that crashed and does not exists anymore
        :return: bool
        """

        processTable = subprocess.check_output('ps aux', shell=True)
        instancesList = json.loads(open(self.app.filesDir+'/instances.json').read())

        if not instancesList:
            return True

        newInstancesList = copy.copy(instancesList)

        for instanceID,data in instancesList.iteritems():
            if not " "+str(instanceID)+" " in processTable:
                del newInstancesList[str(int(instanceID))]

        self.__writeToJSONFile(newInstancesList)
        return True


    def unregister(self, hook=''):
        """
        Unregister self from instances.json
        :return: bool
        """


        if not self.pid:
            return False

        instancesList = json.loads(open(self.app.filesDir+'/instances.json').read())

        if str(self.pid) in instancesList:
            del instancesList[str(self.pid)]

        self.__writeToJSONFile(instancesList)
        return True


    def __writeToJSONFile(self, data):
        w = open(self.app.filesDir+'/instances.json', 'w')
        w.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        w.close()