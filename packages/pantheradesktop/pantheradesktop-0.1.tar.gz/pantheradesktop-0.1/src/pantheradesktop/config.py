import json
import sys
import pantheradesktop.tools as tools

class pantheraConfig:
    """
        Panthera Desktop Configuration
        
        Simple json based key-value storage
        
    """

    panthera = ""
    memory = {}
    configPath = ""
    configurationChanged = False
    strictTypeChecking = True

    def __init__(self, panthera):
        self.panthera = panthera
        self.panthera.hooking.addOption('app.pa_exit', self.save, 1)

    def loadConfig(self):
        """
            Load configuration from JSON file to memory
            
        """

        self.panthera.logging.output("Loading configuration from path " + self.configPath, "pantheraConfig")

        try:
            t = open(self.configPath, "rb")
            self.memory = json.loads(t.read(), object_hook=tools._decode_dict)
        except Exception as e:
            print("Cannot parse configuration file \"" + self.configPath + "\"")
            sys.exit(5)  # errno.EIO = 5

        t.close()


    def getKey(self, key, defaultValue = None, strictTypeChecking = False):
        """
            Get configuration key
        
            key - name
            defaultValue - default value to set if key does not exists yet
        
        """

        if not self.memory:
            self.loadConfig()

        ## if strict value type checking is on we will stick with one data type
        if defaultValue is not None and (self.strictTypeChecking or strictTypeChecking) and key in self.memory:

            if str(type(defaultValue).__name__) != str(type(self.memory[key]).__name__):
                if self.panthera.logging:
                    self.panthera.logging.output('Invalid data type for "'+key+'" key ('+type(defaultValue).__name__+', '+type(self.memory[key]).__name__+')', 'pantheraConfig')

                # set default value in case we have an unexpected type set in configuration file
                self.setKey(key, defaultValue)


        if key in self.memory:
            return self.memory[key]

        ## if key does not exists in key-value database yet, create it with default value
        if defaultValue is not None:
            self.setKey(key, defaultValue)

        return defaultValue


    def setKey(self, key, value):
        """
            Set configuration key

            key - name
            value - value

        """

        if type(key) is not str:
            return False

        if type(value) is type(sys) or type(value) == object:
            return False

        self.configurationChanged = True
        self.memory[key] = value

        if self.getKey('configAutocommit'):
            self.save()


    def exists(self, key):
        """
        Check if key exists
        :param key:
        :return:
        """

        return key in self.memory


    def save(self):
        """
            Save configuration right back to json file

        """

        if self.configurationChanged:
            w = open(self.configPath, "wb")
            w.write(json.dumps(self.memory, sort_keys=True, indent=4, separators=(',', ': ')))
            w.close()