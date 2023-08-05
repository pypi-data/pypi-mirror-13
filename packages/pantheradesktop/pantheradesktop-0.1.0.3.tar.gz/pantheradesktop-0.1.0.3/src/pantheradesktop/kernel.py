#-*- encoding: utf-8 -*-
import os
import sys
import atexit
import pantheradesktop.config
import pantheradesktop.hooking
import pantheradesktop.logging
import pantheradesktop.tools as tools
import pantheradesktop.instance
import pantheradesktop.interactive
import traceback

try:
    import pantheradesktop.interactive
except Exception:
    pass

try:
    import pantheradesktop.argsparsing
except Exception:
    pass

try:
    import pantheradesktop.qtgui
except Exception:
    pass

import pantheradesktop.db

__author__ = "Damian Kęska"
__license__ = "LGPLv3"
__maintainer__ = "Damian Kęska"
__copyright__ = "Copyleft by Panthera Desktop Team"

class Singleton(object):
    _instance = None
    
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
            
        return class_._instance

class pantheraDesktopApplication(Singleton):
    """
       Panthera Desktop Framework
       
       Main class used to be extended by desktop application, provides base functionality (configuration, database, templating)
       
    """

    config = "" # cofiguration object
    interactive = ""
    template = "" # gui template object
    argsParser = ""
    instances = ""
    app = ""
    __appMain = ""
    _plugins = {}
    pluginsLoaded = False
    pluginsAvailable = []

    # application name
    appName = "pantheradesktop-exampleapp"
    version = "0.1"
    
    # directory where to store data eg. ~/.example (will be automaticaly generated in initialize function)
    filesDir = ""
    
    # core classes
    coreClasses = {
        'hooking': pantheradesktop.hooking.pantheraHooking, 
        'logging': pantheradesktop.logging.pantheraLogging, 
        'argsparsing': pantheradesktop.argsparsing.pantheraArgsParsing, 
        'config': pantheradesktop.config.pantheraConfig,
        'gui': pantheradesktop.qtgui.pantheraQTGui, # set to None to disable
        'db': pantheradesktop.db.pantheraDB,
        'instances': '__initialize__',
        'interactive': '__initialize__'
    }
    
    def multipleIsFile(self, dirs, fileName):
        for path in dirs:
            if os.path.isfile(path+"/"+fileName):
                return path+"/"+fileName
                
        return False
    
    @classmethod
    def getInstance(c):
        return c._instance
    
    def initialize(self, quiet=False):
        """
            Create required directories, initialize basic objects
            
        """

        if self.coreClasses['instances'] == '__initialize__' and hasattr(pantheradesktop, 'instance'):
            self.coreClasses['instances'] = pantheradesktop.instance.pantheraJSONInstance

        if self.coreClasses['interactive'] == '__initialize__' and hasattr(pantheradesktop, 'interactive'):
            self.coreClasses['interactive'] = pantheradesktop.interactive.pantheraInteractiveConsole
        
        atexit.register(self.pa_exit)
        self.filesDir = os.path.expanduser("~/."+self.appName)

        # plugins paths
        self.pluginsSearchDirectories = [
            self.filesDir+'/plugins',
            '/usr/share/'+self.appName+'/plugins',
            '/var/lib/'+self.appName+'/plugins'
        ]
        
        # create user's data directory if missing
        if not os.path.isdir(self.filesDir):
            try:
                os.mkdir(self.filesDir)
            except Exception as e:
                print("Cannot create "+self.filesDir+" directory, please check permissions (details: "+e.strerror+")")
                sys.exit(5)

        self.hooking = self.coreClasses['hooking']()
        self.logging = self.coreClasses['logging'](self, quiet)
        
        # plugins support: action before configuration load
        self.hooking.execute('app.beforeConfigLoad')
               
        if not os.path.isfile(self.filesDir+"/config.json"):
            try:
                w = open(self.filesDir+"/config.json", "w")
                w.write("{}")
                w.close()
            except Exception as e:
                print("Cannot create "+self.filesDir+"/config.json, please check permissions (details: "+e.strerror+")")
                sys.exit(5)       
        
        # initialize configuration
        self.config = self.coreClasses['config'](self)
        self.config.configPath = self.filesDir+"/config.json"

        # initialize database
        if self.coreClasses['db']:
            self.db = self.coreClasses['db'](self)


    def togglePlugin(self, pluginName, value=None):
        """
        Toggle plugin on/off
        :param pluginName: Plugin name
        :return: bool
        """

        if not self.pluginsLoaded == True:
            self.loadPlugins()

        plugins = self.config.getKey('plugins', list())

        if (value == False or (value == None and pluginName in plugins)) and pluginName in plugins:
            plugins.remove(pluginName)
        elif value == True or (value == None and pluginName not in plugins):
            plugins.append(pluginName)

        self.config.setKey('plugins', plugins)
        self.config.save()

        return True

    def loadPlugins(self, force=False):
        """
        Load application plugins from directories specified in self.pluginsSearchDirectories
        Only plugins enabled in configuration will be loaded
        :return:
        """

        if self.pluginsLoaded == True and not force:
            return False

        # create a default value for "plugins" key
        self.config.getKey('plugins', list())
        self.config.save()

        self.logging.output('Looking for plugins in: '+str(self.pluginsSearchDirectories), 'pantheraDesktop.plugins')

        for path in self.pluginsSearchDirectories:

            # check only directories that exists in filesystem
            if not os.path.isdir(path):
                continue

            files = os.listdir(path)

            for file in files:
                fileName = os.path.basename(file)
                fileName, fileExtension = os.path.splitext(file)

                if fileExtension.lower() != ".py" or fileName in self._plugins:
                    continue

                # append to list of avaliable plugins
                self.pluginsAvailable.append(fileName)

                if self.config.getKey('plugins') and not fileName in self.config.getKey('plugins'):
                    self.logging.output('Disabling plugin '+fileName, 'pantheraDesktop')
                    continue

                try:
                    self.loadPlugin(fileName, path+"/"+file)

                except Exception as e:
                    self.logging.output('Cannot initialize plugin '+path+'/'+file+', details: '+str(e), 'pantheraDesktop')
                    self.logging.output(traceback.format_exc(), 'pantheraDesktop')

        self.pluginsLoaded = True


    def loadPlugin(self, pluginName, path=None):
        """
        Initialize plugin
        :param pluginName: Plugin name eg. "backup" or "notify"
        :param path: Path to plugins directory /usr/share/copysync/plugins
        :return: object
        """

        if not path:
            for directory in self.pluginsSearchDirectories:
                if pluginName+'.py' in os.listdir(directory):
                    path = directory
                    break

        if not path:
            raise IOError('No such file or directory', 2)

        plugin = tools.include(path)
        self.logging.output('Initializing plugin '+pluginName, 'pantheraDesktop')
        self._plugins[pluginName] = eval("plugin."+pluginName+"Plugin(self)")

        ## call initializePlugin() method if available
        if hasattr(self._plugins[pluginName], 'initializePlugin'):
            self._plugins[pluginName].initializePlugin()

        return self._plugins[pluginName]


    def unloadPlugin(self, pluginName):
        """
        Unload plugin
        :param pluginName: Plugin name eg. "backup" or "notify"
        :return: bool
        """

        if not pluginName in self._plugins:
            return False

        ## execute pre-unload function if exists to clean up some stuff
        if hasattr(self._plugins[pluginName], 'unloadPlugin'):
            self.logging.output('Calling "'+pluginName+'" plugin to deinitialize itself')
            self._plugins[pluginName].unloadPlugin()

        ## try to remove all hooks defined by plugin we want to remove
        self.hooking.removeAllByClass(self._plugins[pluginName].__class__.__name__)

        del self._plugins[pluginName]
        return True


    def main(self, func=None):
        """ Main function """
        
        # validate "instances" module
        if 'instances' in self.coreClasses and callable(self.coreClasses['instances']) and hasattr(self.coreClasses['instances'], 'register'):
            self.logging.output('Registering self instance using '+str(self.coreClasses['instances'])+' instance handler')
            self.instances = self.coreClasses['instances'](self)
            self.instances.register()
            self.instances.cleanup()
            self.hooking.addOption('app.pa_exit', self.instances.unregister)

        if 'interactive' in self.coreClasses and callable(self.coreClasses['interactive']):
            self.logging.output('Initializing interactive mode', 'pantheraDesktop')
            self.interactive = self.coreClasses['interactive'](self)

        # initialize plugins
        self.loadPlugins()

        # initialize args parser
        self.argsParser = self.coreClasses['argsparsing'](self)
        self.argsParser.parse()
        self.hooking.execute('app.argsparsing.init')

        # add default value for configAutocommit
        self.config.getKey('configAutocommit', True)

        self.logging.output('Initializing application mainloop', 'pantheraDesktopApplication')
        
        # graphical user interface (if avaliable)
        if "gui" in self.coreClasses:
            if self.coreClasses['gui']:
                self.gui = self.coreClasses['gui'](self)
        
        # plugins support: mainloop
        self.hooking.execute('app.mainloop')
        
        if hasattr(func, '__call__') or "classobj" in str(type(func)):
            self.__appMain = func(self)


    def pa_exit(self):
        """ On application exit """

        self.logging.output('Got interrupt, finishing jobs and exiting...', 'pantheraDesktop')
        self.hooking.execute('app.pa_exit')
        sys.exit(0)
