# coding: utf-8

from smartbot import Behaviour
from smartbot import ExternalAPI

import re

class TalkBehaviour(Behaviour):
    def __init__(self, bot):
        super(TalkBehaviour, self).__init__(bot)

    def addHandlers(self):
        self.bot.addCommandHandler('talk', self.talk)

    def removeHandlers(self):
        self.bot.removeCommandHandler('talk', self.talk)

    def talk(self, telegramBot, update):
        p = re.compile('([^ ]*) (.*)')
        query = (p.match(update.message.text).groups()[1] or '').strip()
        if query:
            self.logDebug(u'Talk (chat_id: %s, query: %s, source_language: pt)' % (update.message.chat_id, query or 'None'))
            audioFile = ExternalAPI.textToSpeech(query, language='pt', encode='mp3')
            self.bot.sendAudio(chat_id=update.message.chat_id, audio=audioFile, performer=self.bot.getInfo().username)
