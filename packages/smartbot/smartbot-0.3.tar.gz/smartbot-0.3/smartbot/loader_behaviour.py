# coding: utf-8

from smartbot import Behaviour

import re

class LoaderBehaviour(Behaviour):
    def __init__(self, bot, behaviourControl):
        super(LoaderBehaviour, self).__init__(bot)
        self.behaviourControl = behaviourControl

    def addHandlers(self):
        self.bot.addCommandHandler('load', self.loadBehaviour)
        self.bot.addCommandHandler('unload', self.unloadBehaviour)

    def removeHandlers(self):
        self.bot.removeCommandHandler('load', self.loadBehaviour)
        self.bot.removeCommandHandler('unload', self.unloadBehaviour)

    def loadBehaviour(self, telegramBot, update):
        p = re.compile('([^ ]*) (.*)')
        behaviourName = (p.match(update.message.text).groups()[1] or '').strip()
        if behaviourName == 'all':
            self.behaviourControl.loadAll()
        elif self.behaviourControl.getStatus(behaviourName) == 'unloaded':
            self.behaviourControl.load(behaviourName)

    def unloadBehaviour(self, telegramBot, update):
        p = re.compile('(.*) (.*)')
        behaviourName = (p.match(update.message.text).groups()[1] or '').strip()
        if self.behaviourControl.getStatus(behaviourName) == 'loaded':
            self.behaviourControl.unload(behaviourName)
