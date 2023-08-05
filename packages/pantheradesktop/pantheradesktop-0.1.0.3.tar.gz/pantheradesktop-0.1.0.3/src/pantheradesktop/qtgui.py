#-*- encoding: utf-8 -*-
import os
import sys
import json

try:
    from PySide import QtGui, QtCore
except ImportError:
    from PyQt4 import QtGui, QtCore

__author__ = "Damian Kęska"
__license__ = "LGPLv3"
__maintainer__ = "Damian Kęska"
__copyright__ = "Copyleft by Panthera Desktop Team"

class pantheraQTGui:
    panthera = ""
    templatesDir = []
    templates = {}
    app = ""
    startupTemplate = "main" # template to load at startup (leave empty to don't load any template at startup)

    def __init__(self, panthera):
        """
            Initialize class with Panthera object
        """

        self.panthera = panthera
        
        if os.path.isdir("/usr/share/"+self.panthera.appName+"/qtgui"):
            self.templatesDir.append("/usr/share/"+self.panthera.appName+"/qtgui")
        
        if os.path.isdir(os.getcwd()+"/usr"):
            self.templatesDir.append("./usr/share/"+self.panthera.appName+"/qtgui")
            
        self.templatesDir.append(self.panthera.filesDir+"/qtgui")
            
        for path in self.templatesDir:
            sys.path.append(path)
            
        self.app = QtGui.QApplication(sys.argv)
        
        # connect mainloop hook
        self.panthera.hooking.addOption('app.mainloop', self.mainLoop)
        
        
            
    def loadTemplate(self, templateName):
        """
            Compiles UI, save to cache, import cache and driver
            
        """

        # check for source XML file exported from Qt Designer
        uiFile = self.panthera.multipleIsFile(self.templatesDir, "/src/"+templateName+".ui")
        
        if not uiFile:
            raise Exception('Cannot find template source file "' +templateName + '.ui" in templatesDir = '+json.dumps(self.templatesDir)+'/src')
            return False

        # search for compiled Python PyQt4 code     
        cacheFile = self.panthera.multipleIsFile(self.templatesDir, "/cache/"+templateName+".py")
               
        if not cacheFile or os.path.getmtime(uiFile) > os.path.getmtime(cacheFile): # if there is no cache file or it's outdated
            for path in self.templatesDir:
                try:
                    # try to compile the file using pyuic4 and place in writable directory
                    os.system("pyuic4 -x "+uiFile+" > "+path+"/cache/"+templateName+".py")
                except Exception as e:
                    pass
                    
                if os.path.isfile(path+"/cache/"+templateName+".py"):
                    self.panthera.logging.output("Compiled template to '"+path+"/cache/"+templateName+".py'", 'pantheraQTGui')
                    break
    
        try:
            exec("import cache."+templateName+" as templateModule")
        except Exception as e:
            raise Exception('Cannot load template '+templateName+'.py from any path provided in templatesDir = '+json.dumps(self.templatesDir)+'/cache')
            return False # just in case
            
        try:
            exec("import drivers."+templateName+" as templateDriver")
        except Exception as e:
            raise Exception('Cannot load template driver '+templateName+'.py from any path provided in templateDir = '+json.dumps(self.templatesDir)+'/drivers (Exception: '+str(e)+')')
            
        self.templates[templateName] = {'module': templateModule, 'driver': templateDriver.templateMain(templateModule, self.panthera)}
        return self.templates[templateName]['driver']
         
    def mainLoop(self, data=''):
        """
            Main loop hook
            
        """
        
        if self.startupTemplate:
            template = self.loadTemplate(self.startupTemplate)
            template.show()

        try:
            sys.exit(self.app.exec_())
            sys.exit(0)
        except KeyboardInterrupt:
            sys.exit(0)        


class pantheraTemplateDriver:
    viewModule = ""
    view = ""
    panthera = ""

    def __init__(self, view, panthera):
        self.viewModule = view
        self.panthera = panthera
        
        for attribute in dir(view):
            if "Ui_" in attribute:
                self.panthera.logging.output('Found GUI class "'+attribute+'"', 'pantheraTemplateDriver')
                exec("self.view = view."+attribute+"()")
                self.initializeView()
                
    def initializeView(self):
        """
            Initialize view
        """

        pass
                
    def show(self):
        self.panthera.logging.output('Showing QMainWindow', 'pantheraTemplateDriver')
        self.window = QtGui.QMainWindow()
        self.view.setupUi(self.window)
        self.window.show()
