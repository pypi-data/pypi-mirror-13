# coding: utf-8

from smartbot import Utils

import time

class Behaviour(object):
    def __init__(self, bot):
        self.bot = bot
        self.loaded = False

    def load(self):
        if not self.loaded:
            try:
                self.addHandlers()
                self.loaded = True
                self.logDebug('Behaviour loaded')
                self.onLoad()
            except Warning as warn:
                self.logWarning(warn.message)

    def unload(self):
        if self.loaded:
            self.removeHandlers()
            self.loaded = False
            self.logDebug('Behaviour unloaded')
            self.onUnload()

    def logDebug(self, message):
        Utils.logDebug(self.bot, self.__class__.__name__, message)

    def logWarning(self, message):
        Utils.logWarning(self.bot, self.__class__.__name__, message)

    def onLoad(self):
        None

    def onUnload(self):
        None

    def addHandlers(self):
        None

    def removeHandlers(self):
        None
