# coding: utf-8

import io
import requests

class Bot(object):
    def __init__(self, token, adminId=None):
        self.adminId = adminId
        self.token = token

    def getInfo(self):
        raise NotImplementedError

    def addMessageHandler(self, handler):
        raise NotImplementedError

    def removeMessageHandler(self, handler):
        raise NotImplementedError

    def addCommandHandler(self, command, handler):
        raise NotImplementedError

    def removeCommandHandler(self, command, handler):
        raise NotImplementedError

    def sendMessage(self, **kargs):
        raise NotImplementedError

    def sendVoice(self, **kargs):
        raise NotImplementedError

    def sendAudio(self, **kargs):
        raise NotImplementedError

    def dispatchMessage(self, update):
        raise NotImplementedError

    def dispatchRegex(self, update):
        raise NotImplementedError

    def dispatchCommand(self, update, command):
        raise NotImplementedError

    def listen(self):
        raise NotImplementedError
