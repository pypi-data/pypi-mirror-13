# coding: utf-8

from smartbot import Behaviour
from smartbot import ExternalAPI

import re

class TranslateBehaviour(Behaviour):
    def __init__(self, bot):
        super(TranslateBehaviour, self).__init__(bot)

    def addHandlers(self):
        self.bot.addCommandHandler('translateen', self.translateen)
        self.bot.addCommandHandler('translatept', self.translatept)

    def removeHandlers(self):
        self.bot.removeCommandHandler('translateen', self.translateen)
        self.bot.removeCommandHandler('translatept', self.translatept)

    def translateen(self, telegramBot, update):
        p = re.compile('([^ ]*) (.*)')
        query = (p.match(update.message.text).groups()[1] or '').strip()
        if query:
            self.logDebug(u'Translate (chat_id: %s, query: %s, source_language: en)' % (update.message.chat_id, query or 'None'))
            result = ExternalAPI.translate(query, 'en', 'pt')
            self.bot.sendMessage(chat_id=update.message.chat_id, text=result)

    def translatept(self, telegramBot, update):
        p = re.compile('([^ ]*) (.*)')
        query = (p.match(update.message.text).groups()[1] or '').strip()
        if query:
            self.logDebug(u'Translate (chat_id: %s, query: %s, source_language: pt)' % (update.message.chat_id, query or 'None'))
            result = ExternalAPI.translate(query, 'pt', 'en')
            self.bot.sendMessage(chat_id=update.message.chat_id, text=result)
