from pantheradesktop import pantheraClass
import pantheradesktop.tools as tools
import sys
import os
from code import InteractiveConsole

class Console(InteractiveConsole):
    def __init__(*args): InteractiveConsole.__init__(*args)

class pantheraInteractiveConsole(pantheraClass):
    thread = None
    worker = None

    ## put here your console shortcuts
    recognizedChars = {
        'q': 'pa_exit'
    }

    def main(self):
        """
        Main function that registers base shortcuts and starts a thread
        :return:
        """

        self.recognizedChars['q'] = self.app.pa_exit
        self.recognizedChars['l'] = self.clearConsole
        self.recognizedChars['p'] = self.pythonConsole
        self.thread, self.worker = tools.createThread(self.interactiveConsole)


    def clearConsole(self):
        """
        Clear console screen
        :return:
        """

        os.system('clear')


    def pythonConsole(self):
        """
        Starts an interactive Python console
        :return:
        """

        app = panthera = self.app

        vars = globals().copy()
        vars.update(locals())
        console = Console(vars)
        console.interact()


    def interactiveConsole(self, thread=''):
        """
        Interactive console loop thread
        :param thread:
        :return:
        """

        while True:
            char = sys.stdin.read(1)

            if char and char in self.recognizedChars:
                self.recognizedChars[char]()
