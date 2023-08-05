# coding: utf-8

from smartbot import Behaviour
from smartbot import ExternalAPI

import re

class EviBehaviour(Behaviour):
    def __init__(self, bot):
        super(EviBehaviour, self).__init__(bot)

    def addHandlers(self):
        self.bot.addCommandHandler('evi', self.evi)

    def removeHandlers(self):
        self.bot.removeCommandHandler('evi', self.evi)

    def query(self, queryEnglish):
        return ExternalAPI.eviQuery(queryEnglish)

    def evi(self, telegramBot, update):
        p = re.compile('([^ ]*) (.*)')
        queryEnglish = (p.match(update.message.text).groups()[1] or '').strip()
        self.logDebug(u'Evi query (chat_id: %s, query: %s)' % (update.message.chat_id, queryEnglish or 'None'))
        answerEnglish = self.query(queryEnglish)
        answerEnglish = (answerEnglish or '').replace('\n', '. ')
        if answerEnglish:
            self.bot.sendMessage(chat_id=update.message.chat_id, text=answerEnglish)
        else:
            self.bot.sendMessage(chat_id=update.message.chat_id, text=u'Não entendi')
