import os, urllib2, urllib, shutil, zipfile, subprocess, webbrowser, socket, smtplib
import time
from time import sleep
import datetime
import imaplib
import email
import pkgutil
import requests
from random import randint
from email.Message import Message
from os.path import expanduser
from datetime import datetime, time

class Core():
    def __init__(self):

        self.path = "{0}/{1}".format(expanduser("~"), "Asher")
        self.helper = 'helper.info'

        #All the colors
        self.c_end = '\033[0m'
        self.c_blu = '\033[1;36m'
        self.c_red = '\033[1;31m'
        self.c_gry = '\033[90m'

        self.emails = {} # This is for all the messages recieved via email.
        self.messages = {} # This is for all the messages recieved via socket.

        self.all = [] # Keeps log of all items in the file, for when we re-write it.
        self.record = [] # Keeps the order in which they came in...

        #Everything for the plugins...
        self.swap_words = {}
        self.key_words = {}
        self.responses = {}
        self.responseNum = {}
        self.opener = {}
        self.Global_Plugins = {}

        self.devMode = False

        self.startUp()

    def startUp(self):
        self.load()
        while True:
            self.loadThem()
            if len(self.all) > 0:
                data = self.readThem().split('$$')
                newData = self.respondThem(str(data[0]))
                self.decidedThem(str(newData), str(data[1]))
                self.deleteThem()
            else:
                pass

    def loadThem(self):
        self.emails = {}
        self.message = {}
        self.all = []
        self.record = []
        with open("{0}/{1}".format(self.path, self.helper), 'r') as _in:
            for line in _in:
                tokens = line.split('$$')
                if str(tokens[1]) == 'true':
                    self.emails[str(tokens[0])] = str(tokens[2])
                    self.record.append('email')
                else:
                    self.messages[str(tokens[0])] = str(tokens[2])
                    self.record.append('message')
                self.all.append(line)

    def readThem(self):
        toRead = str(self.record[0])
        if str(toRead) == 'email':
            # The latest one is an email... so we will read that first.
            self.log('email', 'false', self.all[0].strip())
            item = self.emails.keys()[0] # This will get us the first item in the dictionary.
            return '{0}$${1}'.format(item, 'email')
        else:
            # The latest one is a message... so we will read that first.
            self.log('message', 'false', self.all[0].strip())
            item = self.messages.keys()[0] # This will get us the first item in the dictionary.
            return '{0}$${1}'.format(item, 'message')

    def respondThem(self, dataIn):
        self.log('none', 'false', '...')
        self.log('none', 'false', 'in: {0}'.format(str(dataIn)))
        self.log('none', 'false', '...')
        _string = ''
        command = str(dataIn).strip()

        for module in self.modules:
            foundWords = []
            commandWords = []
            needed = 0
            if '|' in self.key_words[module]:
                for word in self.key_words[module].split(' | '):
                    if not word == '$x':
                        commandWords.append(word)
                    needed += 1
            else:
                commandWords.append(self.key_words[module])
                needed += 1

            if '|' in self.swap_words[module]:
                for word in self.swap_words[module].split(' | '):
                    if not word == '':
                        commandWords.append(word)
            else:
                if not self.swap_words[module] == '':
                    commandWords.append(word)

            for word in commandWords:
                if str(word) in command:
                    foundWords.append(str(word))

            if len(foundWords) == needed:
                try:
                    responses = []
                    if str(module) in self.responses:
                        for response in self.responses[module].split(' | '):
                            responses.append(response)
                        chosen = randint(0, len(responses)-1)
                        if _string:
                            _string += ". {0}".format(responses[int(chosen)])
                        else:
                            _string = responses[int(chosen)]
                    if self.Global_Plugins[str(module).lower()] == 'true':
                        data = self.plugins[module].execute(command)
                        if _string:
                            _string += ". {0}".format(str(data))
                        else:
                            _string = str(data)
                except:
                    print("[ERROR] There has been an error when running the {0} module".format(self.plugins[module].moduleName))
        if _string:
            self.log('none', 'false', 'out: {0}'.format(_string))
            return str(_string).lower().strip()


    def decidedThem(self, response, item):
        if str(item) == 'message':
            if not str(response).lower() == 'none':
                clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                clientsocket.connect((str('localhost'), int(5000)))
                clientsocket.send(str(response))
                self._speak(str(response))


    def deleteThem(self):
        toDel = str(self.record[0])
        if str(toDel) == 'email':
            self.log('email', 'true', self.all[0])
            del self.emails[str(self.emails.keys()[0])]
        else:
            self.log('message', 'true', self.all[0])
            del self.messages[str(self.messages.keys()[0])]
        del self.all[0]
        with open("{0}/{1}".format(self.path, self.helper), 'w') as out:
            for item in self.all:
                out.write(item)

    def answered(self, item):
        if str(item) in self.all:
            # This means that it is in the file, so now we can remove it.
            val = self.all.index(str(item))
            del self.all[int(val)]

    def load(self):
        self.modules = []
        try:
            resp = self.mods()
        except:
            resp = '404'
        if not resp == '404':

            holder_modules_opener = []
            holder_modules_closer = []
            for line in resp.json():
                if str(line['opener']).lower == "true":
                    holder_modules_opener.apppend(line['name'].lower())
                else:
                    holder_modules_closer.append(line['name'].lower())
                self.swap_words[line['name'].lower()] = line['swaps'].lower()
                self.key_words[line['name'].lower()] = line['keyWords'].lower()
                self.responses[line['name'].lower()] = line['responses'].lower()
                self.responseNum[line['name'].lower()] = line['possibleResponses'].lower()
                self.opener[line['name'].lower()] = str(line['opener']).lower()
                self.Global_Plugins[str(line['name']).lower()] = 'false'
            for item in holder_modules_opener:
                self.modules.append(item)
            for item in holder_modules_closer:
                self.modules.append(item)
            print("\n")
        self.getPlugins()

    def getPlugins(self):
        """Try to load all modules found in the modules folder"""
        path = os.path.join(os.path.dirname(__file__), "plugins")
        directory = pkgutil.iter_modules(path=[path])
        self.plugins = {}
        for finder, name, ispkg in directory:
            try:
                loader = finder.find_module(name)
                module = loader.load_module(name)
                if hasattr(module, "commandWords") \
                        and hasattr(module, "swapWords") \
                        and hasattr(module, "moduleName") \
                        and hasattr(module, "execute"):
                    self.swap_words[str(name)] = module.swapWords
                    self.key_words[str(name)] = module.commandWords
                    self.Global_Plugins[str(name)] = 'true'
                    self.modules.append(name)
                    self.plugins[str(name)] = module
                    print("The module '{0}' has been loaded, "
                          "successfully.".format(name))
                else:
                    print("[ERROR] The module '{0}' is not in the "
                          "correct format.".format(name))
            except:
                print("[ERROR] The module '" + name + "' has some errors.")
        print("\n")


    def _speak(self, _toSay):
        cmd = ['~/talk', _toSay]

        subprocess.call(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def _url(self, path):
        return 'http://localhost:8080' + path

    def mods(self):
        return requests.get(self._url('/mods/'))

    def log(self, item, delete, details):
        try:
            tokens = details.split('$$')
        except:
            pass
        if str(item) == 'email':
            email = tokens[2].split('@')
            if str(delete) == 'true':
                print('[{0}-{2}]{3}Deleted email from {1}{2}\n\n'.format(self.c_red, email[0].strip(), self.c_end, self.c_gry))
            else:
                print('[{0}+{2}]{3}Got an email from {1}{2}'.format(self.c_blu, email[0].strip(), self.c_end, self.c_gry))
        elif str(item) == 'message':
            name = tokens[2]
            if str(delete) == 'true':
                print('[{0}-{2}]{3}Deleted a message from {1}{2}\n\n'.format(self.c_red, name.strip(), self.c_end, self.c_gry))
            else:
                print('[{0}+{2}]{3}Got a message from {1}{2}'.format(self.c_blu, name.strip(), self.c_end, self.c_gry))
        elif str(item) == 'error':
            print('An error occured: \n{0}'.format(details))
        elif str(item) == 'none':
            print('   {0}{1}{2}'.format(self.c_gry, details, self.c_end))


if __name__ == "__main__":
    app = Core()
