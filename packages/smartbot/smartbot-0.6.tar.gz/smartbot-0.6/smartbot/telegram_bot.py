# coding: utf-8

import io
import requests
import telegram
from smartbot import Bot
from smartbot import Utils

class TelegramBot(Bot):
    def __init__(self, token, adminId=None):
        super(TelegramBot, self).__init__(token, adminId)
        self.baseUrl = 'https://api.telegram.org/bot%s' % token
        self.telegramBot = telegram.Bot(token=token)
        self.updater = telegram.Updater(token=token)
        self.dispatcher = self.updater.dispatcher
        self.info = None

    def getInfo(self):
        self.info = self.info or self.telegramBot.getMe()
        return self.info

    def addMessageHandler(self, handler):
        self.dispatcher.addTelegramMessageHandler(handler)

    def removeMessageHandler(self, handler):
        self.dispatcher.removeTelegramMessageHandler(handler)

    def addCommandHandler(self, command, handler):
        self.dispatcher.addTelegramCommandHandler(command, handler)

    def removeCommandHandler(self, command, handler):
        self.dispatcher.removeTelegramCommandHandler(command, handler)

    def sendMessage(self, **kargs):
        Utils.logDebug(self, self.__class__.__name__, 'sendMessage %s' % kargs)
        self.telegramBot.sendMessage(**kargs)

    def sendVoice(self, **kargs):
        files = { 'chat_id': ('', io.StringIO(unicode(str(kargs['chat_id'])))),
                'voice': ('voice.ogg', open(kargs['voice'], 'rb'), 'application/octet-stream') }
        requests.post('%s/sendVoice' % self.baseUrl, files=files)

    def sendAudio(self, **kargs):
        files = { 'chat_id': ('', io.StringIO(unicode(str(kargs['chat_id'])))),
                'performer': ('', io.StringIO(unicode(str(kargs.get('performer') or 'bot')))),
                'title': ('', io.StringIO(unicode(str(kargs.get('title') or 'talk')))),
                'mime_type': ('', io.StringIO(u'audio/mpeg')),
                'audio': ('audio.mp3', open(kargs['audio'], 'rb'), 'application/octet-stream') }
        requests.post('%s/sendAudio' % self.baseUrl, files=files)

    def dispatchMessage(self, update):
        self.dispatcher.dispatchTelegramMessage(update)

    def dispatchRegex(self, update):
        self.dispatcher.dispatchTelegramRegex(update)

    def dispatchCommand(self, update, command):
        self.dispatcher.dispatchTelegramCommand(update)

    def listen(self):
        self.updater.start_polling()
