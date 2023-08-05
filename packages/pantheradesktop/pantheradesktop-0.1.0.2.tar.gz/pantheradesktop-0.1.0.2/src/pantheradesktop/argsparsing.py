#-*- encoding: utf-8 -*-

import pantheradesktop.tools as tools
import argparse
import sys
import os

__author__ = "Damian Kęska"
__license__ = "LGPLv3"
__maintainer__ = "Damian Kęska"
__copyright__ = "Copyleft by Panthera Desktop Team"

class pantheraArgsParsing:
    """
        Arguments parsing class for Panthera Desktop Framework
        It's just a simple wrapper to argparse module that supports callbacks
        
    """

    description = 'Example app'
    argparse = ""
    panthera = None
    app = None
    
    # here will be args and opts stored
    args = None
    opts = None

    # plugins management
    _enablePluginsManagement = True
    _enableConfigManagement = True
    _enableDebugArgs = True
    _enableDaemonizeArgs = True

    knownArgs = {}

    def __init__ (self, panthera):
        """
            Initialize argument parser with Panthera Framework object
            
            panthera - Panthera object
        """

        self.panthera = panthera
        self.app = panthera

        self.appendStaticArguments()
        self.argparse = argparse.ArgumentParser(description=self.description)
        self.createArgument('--version', self.version, 'Display help', action='store_true', required=False)

        if self._enablePluginsManagement:
            self.createArgument('--plugins', self.pluginsList, 'Display plugins list', action='store_true', required=False)
            self.createArgument('--plugins-enable', self.pluginsEnable, 'Enable plugin', required=False)
            self.createArgument('--plugins-disable', self.pluginsDisable, 'Enable plugin', required=False)

        if self._enableConfigManagement:
            self.createArgument('--config', self.configKeys, 'List configuration keys', action='store_true', required=False)
            self.createArgument('--config-set', self.configSetKey, 'Set configuration key value', required=False)
            self.createArgument('--config-get', self.configGetKey, 'Get configuration value', required=False)

        if self._enableDebugArgs:
            self.createArgument('--debug', self.setDebuggingMode, '', 'Enable debugging mode', required=False, action='store_false')

        if self._enableDaemonizeArgs:
            self.createArgument('--daemonize', self.setDaemonMode, '', 'Enable debugging mode', required=False, action='store_false')

        # @hook app.argsparsing.__init__.after self
        self.app.hooking.execute('app.argsparsing.__init__.after', self)


    def appendStaticArguments(self):
        """
        Append static arguments from configuration key "panthera.argsparsing.defaultArgs"

        :return: None
        """

        if self.app.config.getKey('panthera.argsparsing.defaultArgs', ''):
            sys.argv = sys.argv + self.app.config.getKey('panthera.argsparsing.defaultArgs').split(' ')

    def setDaemonMode(self, opt = ''):
        """
        Run application in daemon mode
        :param opt:
        :return:
        """

        if not os.path.isdir(self.panthera.filesDir + '/logs'):
            os.mkdir(self.panthera.filesDir + '/logs')

        tools.daemonize(stdout = self.panthera.filesDir + '/logs/stdout', stderr = self.panthera.filesDir + '/logs/stderr')


    def setDebuggingMode(self, opt = ''):
        """
        Enable debugging mode
        :param opt:
        :return:
        """

        self.app.logging.silent = False
        self.app.logging.flushAndEnablePrinting()


    def configKeys(self, opt=''):
        """
        List all configuration keys
        :param opt:
        :return:
        """

        self.app.config.loadConfig()
        print(self.app.config.memory)
        sys.exit(0)

    def configSetKey(self, key=''):
        """
        Set a configuration key
        :param key: Configuration key name or xpath
        :return:
        """

        self.app.config.loadConfig()

        if not len(self.opts):
            sys.exit(1)

        self.app.config.setKey(key, self.opts[0])
        self.app.config.save()

        sys.exit(0)

    def configGetKey(self, key=''):
        """
        Get configuration key
        :param key: Key name or xpath
        :return:
        """

        self.app.config.loadConfig()

        if self.app.config.exists(key):
            print(self.app.config.getKey(str(key)))
            sys.exit(0)
        else:
            sys.exit(1)

    def pluginsEnable(self, pluginName='', enable=True):
        """
        Enable a plugin
        :param pluginName:
        :param enable:
        :return:
        """

        self.app.loadPlugins()

        if not pluginName in self.app.pluginsAvailable:
            print("Cannot toggle plugin: "+str(pluginName)+", file not found")
            sys.exit(1)

        self.app.togglePlugin(pluginName, enable)
        sys.exit(0)

    def pluginsDisable(self, pluginName):
        """
        Disable a plugin
        :param pluginName:
        :return:
        """

        return self.pluginsEnable(pluginName, False)

    def pluginsList(self, opt=''):
        """
        List all plugins (enabled and disabled)
        :param opt:
        :return:
        """

        self.app.loadPlugins()

        print("Application is looking for plugins in those directories: ")

        for directory in self.app.pluginsSearchDirectories:
            print(directory)

        print("\n")

        if self.app.pluginsAvailable:
            print("Available plugins: ")

            for plugin in self.app.pluginsAvailable:
                if plugin in self.app._plugins:
                    print("[x] "+plugin)
                else:
                    print("[ ] "+plugin)

            print("\nx - enabled")
        else:
            print("No plugins available\n")

        sys.exit(0)
        
    def version(self, value=''):
        """
            Example argument handler, shows application version
            
        """

        self.app.hooking.execute('app.argsparsing.version', self)
        print(self.panthera.appName + " " +self.panthera.version)
        sys.exit(0)
        
        
        
    def createArgument(self, arg, callback, default="", help="", required=False, dataType=None, action='store', choices=None, type=None, skipArgParse=False, short=None):
        """
            Add argument to list of known arguments
            
            arg - Argument name eg. --test
            callback - Function to call back if this argument was used
            default - Default value
            help - Help text to display
            required - Is this a required field?
            skipArgParse - Skip using argparse in this function and use it by your own
            
            Returns none
        """
        
        self.knownArgs[arg] = callback
        argsString = 'arg, default=default, help=help, required=required, action=action'

        if not skipArgParse:
            if not action == 'store_true' and not action == 'store_const' and not action == 'store_false':
                argsString += ', choices=choices, type=type'

            if short is not None:
                argsString = 'short, '+argsString

            eval('self.argparse.add_argument('+argsString+')')

        
    def parse(self):
        """
            Run arguments parsing
            
        """
        
        if "addArgs" in dir(self):
            self.addArgs()

            # @hook app.argsparsing.parse.addArgs self
            self.app.hooking.execute('app.argsparsing.parse.addArgs', self)
        
        self.args = self.argparse.parse_known_args()
        self.opts = self.args[1]

        # @hook app.argsparsing.parse.before self
        self.app.hooking.execute('app.argsparsing.parse.before', self)

        for arg in self.knownArgs:
            if arg in sys.argv:
                self.knownArgs[arg](self.args[0].__dict__[arg.replace('--', '').replace('-', '_')])

        # @hook app.argsparsing.parse.after self
        self.app.hooking.execute('app.argsparsing.parse.after', self)