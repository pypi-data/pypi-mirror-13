# coding: utf-8

from smartbot import Behaviour
from smartbot import ExternalAPI

import re
import random

class NasaBehaviour(Behaviour):
    def __init__(self, bot):
        super(NasaBehaviour, self).__init__(bot)

    def addHandlers(self):
        self.bot.addCommandHandler('nasa', self.nasaSearch)

    def removeHandlers(self):
        self.bot.removeCommandHandler('nasa', self.nasaSearch)

    def nasaSearch(self, telegramBot, update):
        self.logDebug(u'Nasa search (chat_id: %s)' % update.message.chat_id)
        nasaData = ExternalAPI.getNasaIOD()
        if nasaData:
            self.bot.sendMessage(chat_id=update.message.chat_id, text=nasaData['imageSource'])
            self.bot.sendMessage(chat_id=update.message.chat_id, text=nasaData['explanation'])
        else:
            self.bot.sendMessage(chat_id=update.message.chat_id, text='Não encontrei imagem da nasa')
