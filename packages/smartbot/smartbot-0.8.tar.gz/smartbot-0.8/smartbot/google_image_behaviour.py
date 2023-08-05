# coding: utf-8

from smartbot import Behaviour
from smartbot import ExternalAPI

import re

class GoogleImageBehaviour(Behaviour):
    def __init__(self, bot):
        super(GoogleImageBehaviour, self).__init__(bot)

    def addHandlers(self):
        self.bot.addCommandHandler('gimage', self.imageSearch)

    def removeHandlers(self):
        self.bot.removeCommandHandler('gimage', self.imageSearch)

    def imageSearch(self, telegramBot, update):
        p = re.compile('([^ ]*) (.*)')
        query = (p.match(update.message.text).groups()[1] or '').strip()
        self.logDebug(u'Google image search (chat_id: %s, query: %s)' % (update.message.chat_id, query or 'None'))
        imageSources = ExternalAPI.searchGoogleImage(query)
        if imageSources:
            self.bot.sendMessage(chat_id=update.message.chat_id, text=imageSources[0])
        else:
            self.bot.sendMessage(chat_id=update.message.chat_id, text=u'Não encontrei imagem relacionada')
