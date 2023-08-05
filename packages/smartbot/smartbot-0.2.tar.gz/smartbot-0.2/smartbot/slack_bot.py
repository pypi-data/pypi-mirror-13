# coding: utf-8

import io
import re
import sys
import time
import json
import datetime
import requests
import slackclient
from smartbot import Bot
from smartbot import Utils

class DynObject(object):
    pass

class SlackBot(Bot):
    def _getChannelInfo(self, channel):
        if not self._channelInfoCache.get(channel) or (datetime.datetime.now() - datetime.datetime.fromtimestamp(float(self._channelInfoCache[channel]['last_read']))).total_seconds > 300:
            self._channelInfoCache[channel] = json.loads(self.slackClient.api_call('channels.info', channel=channel)).get('channel')
        return self._channelInfoCache.get(channel)

    def __init__(self, token, adminId=None):
        super(SlackBot, self).__init__(token, adminId)
        self.baseUrl = 'https://slack.com/api'
        self.slackClient = slackclient.SlackClient(token)
        self._commandMatcher = re.compile('^_(\w+)( .*)?$')
        self._channelInfoCache = {}
        self._messageHandlers = []
        self._regexHandlers = []
        self._commandHandlers = []
        self._mentionMacher = None
        self._info = None

    def getInfo(self):
        if not self._info:
            slackInfo = json.loads(self.slackClient.api_call('auth.test'))
            self._info = DynObject()
            self._info.id = slackInfo.get('user_id')
            self._info.username = self._info.first_name = slackInfo.get('user')
        return self._info

    def addMessageHandler(self, handler):
        if not self._mentionMacher:
            info = self.getInfo()
            self._mentionMacher = re.compile('.*(^|\W)@?(%s|%s)(\W|$).*' % (info.id, info.username), re.IGNORECASE)
        # self._messageHandlers.append((handler,))
        self.addRegexHandler(self._mentionMacher, handler)

    def removeMessageHandler(self, handler):
        # self._messageHandlers.remove((handler,))
        self.removeRegexHandler(self._mentionMacher, handler)

    def addRegexHandler(self, matcher, handler):
        self._regexHandlers.append((matcher, handler))

    def removeRegexHandler(self, matcher, handler):
        self._regexHandlers.remove((matcher, handler))

    def addCommandHandler(self, command, handler):
        self._commandHandlers.append((command, handler))

    def removeCommandHandler(self, command, handler):
        self._commandHandlers.remove((command, handler))

    def sendMessage(self, **kargs):
        channel = kargs.get('chat_id')
        text = kargs.get('text') or ''
        Utils.logDebug(self, self.__class__.__name__, 'sendMessage %s' % kargs)
        self.slackClient.api_call('chat.postMessage', channel=channel, as_user=True, username=self.getInfo().username, icon_emoji=':robot_face:', text=text.encode('utf-8'))

    def sendFile(self, **kargs):
        channel = kargs.get('chat_id')
        filename = kargs.get('filename') or 'file'
        filetype = kargs.get('filetype') or 'txt'
        params = { 'token': self.token,
                'channels': channel,
                'title': kargs.get('title') or 'file'
                }
        files = { 'file': (filename, open(kargs['file'], 'rb'), 'application/octet-stream') }
        return requests.post('%s/files.upload' % self.baseUrl, data=params, files=files)

    def sendVoice(self, **kargs):
        kargs['file'] = kargs.get('voice')
        kargs['filename'] = 'voice.ogg'
        kargs['filetype'] = 'ogg'
        self.sendFile(**kargs)

    def sendAudio(self, **kargs):
        kargs['file'] = kargs.get('audio')
        kargs['filename'] = 'audio.mp3'
        kargs['filetype'] = 'mp3'
        self.sendFile(**kargs)

    def dispatchMessage(self, update):
        dispatched = False
        for messageHandler in self._messageHandlers:
            handler = messageHandler[0]
            handler(self, update)
            dispatched = True
        return dispatched

    def dispatchRegex(self, update):
        dispatched = False
        for regexHandler in self._regexHandlers:
            regex = regexHandler[0]
            handler = regexHandler[1]
            if regex.match(update.message.text):
                handler(self, update)
                dispatched = True
        return dispatched

    def dispatchCommand(self, update, command=None):
        dispatched = False
        commandMatches = self._commandMatcher.match(update.message.text)
        if command or commandMatches:
            for commandHandler in self._commandHandlers:
                commandCurrent = commandHandler[0]
                handler = commandHandler[1]
                if command == commandCurrent or (commandMatches and commandCurrent == commandMatches.groups()[0]):
                    handler(self, update)
                    dispatched = True
        return dispatched

    def processUpdate(self, update):
        if update.type == 'message':
            info = self.getInfo()
            channelInfo = self._getChannelInfo(update.message.chat_id)
            maxMembers = 4
            if update.message.user == self.adminId or (channelInfo and len(channelInfo['members'])) >= maxMembers:
                if not (update.message.user == self.adminId and self.dispatchCommand(update)):
                    self.dispatchMessage(update)
                    self.dispatchRegex(update)
            else:
                self.sendMessage(chat_id=update.message.chat_id, text=u'Sinto muito. Só estou autorizado a interagir nos canais com pelo menos %s membros.' % maxMembers)

    def convertToUpdate(self, slackEvent):
        update = DynObject()
        if slackEvent.get(u'text') and slackEvent.get(u'type') == 'message' and not slackEvent.get(u'subtype') == 'bot_message' and not slackEvent.get(u'user') == self.getInfo().id:
            update.type = 'message'
            update.message = DynObject()
            update.message.user = slackEvent.get(u'user')
            update.message.text = slackEvent.get(u'text') or ''
            update.message.chat_id = slackEvent.get(u'channel')
        else:
            update.type = 'unknown'
        return update

    def listen(self):
        lastPing = datetime.datetime.now()
        if self.slackClient.rtm_connect():
            while True:
                events = self.slackClient.rtm_read()
                for event in events:
                    self.processUpdate(self.convertToUpdate(event))
                if (datetime.datetime.now() - lastPing).total_seconds() > 60:
                    self.slackClient.server.ping()
                    lastPing = datetime.datetime.now()
                time.sleep(0.5)
        # try:
        # except:
        #     Utils.logError(self, self.__class__.__name__, sys.exc_info())
