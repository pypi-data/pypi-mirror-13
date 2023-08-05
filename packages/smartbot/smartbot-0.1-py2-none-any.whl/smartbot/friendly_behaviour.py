# coding: utf-8

from smartbot import Behaviour
from smartbot import ExternalAPI

import re
import os
import random
from threading import Thread

class DynObject(object):
    pass

class FriendlyBehaviour(Behaviour):
    __active_chats = []

    def __init__(self, bot, behaviourControl, vocabulary={}):
        super(FriendlyBehaviour, self).__init__(bot)
        self.behaviourControl = behaviourControl
        self.vocabulary = vocabulary
        self._defaultAnswers = [
              u'Prefiro não comentar',
              u'Não tenho informações suficientes na minha base para responder',
              u'Não sei (ainda)',
              u'Estou em fase de crescimento',
              u'Me pergunte amanhã'
            ]

    def addHandlers(self):
        info = self.bot.getInfo()
        self.botInfo = info
        self.mentionMatcher = re.compile('.*(^|\W)@?(%s|%s)(\W|$).*' % (info.id, info.username), re.IGNORECASE)
        self.bot.addMessageHandler(self.mention)

    def removeHandlers(self):
        self.bot.removeMessageHandler(self.mention)

    def mention(self, telegramBot, update):
        message = update.message.text
        words = re.compile('\s+', re.UNICODE).split(message)
        words = filter(lambda word: word.strip() and not self.mentionMatcher.match(word), words)
        words = map(lambda word: word.lower(), words)
        aliases = self.vocabulary.get('aliases')
        if aliases and len(words) >= 1 and words[0] in aliases.keys():
            command = aliases[words[0]]
            params = words[1:]
            self.logDebug(u'Friendly mention (chat_id: %s, command: %s, params: %s)' % (update.message.chat_id, command, (' ').join(params or ['None'])))
            updateMock = DynObject()
            updateMock.message = DynObject()
            if (hasattr(update.message, 'user')):
                updateMock.message.user = update.message.user
            updateMock.message.chat_id = update.message.chat_id
            updateMock.message.text = '/%s %s' % (command, ' '.join(params))
            self.bot.dispatchCommand(updateMock, command)
        elif len(words) == 1:
            self.bot.sendMessage(chat_id=update.message.chat_id, text=u'Não entendi')
        elif len(words) > 1:
            sentence = ' '.join(words)
            bc = self.behaviourControl
            results = []
            sentenceEnglish = ExternalAPI.translate(sentence, fromLanguage='pt') or ''
            target = lambda behaviour, sentence: bc.getStatus(behaviour) == 'loaded' and results.append({'source': behaviour, 'answer': bc.get(behaviour).query(sentence)})
            t1 = Thread(target=target, args=('evi', sentenceEnglish))
            t2 = Thread(target=target, args=('wolfram', sentenceEnglish))
            map(lambda t: t.start(), [t1, t2])
            map(lambda t: t.join(), [t1, t2])
            results = filter(lambda result: result['answer'] and result['answer'].strip(), results)
            results = sorted(results, lambda x, y: len(x['answer']) - len(y['answer']))
            if results:
                result = results[0]
                self.logDebug(u'Friendly answer (chat_id: %s, sentence: %s, sentenceEnglish: %s, answers: %s, choosen: %s)' % (update.message.chat_id, sentence, sentenceEnglish, results, result['source']))
                answerEnglish = result['answer']
                replacements = self.vocabulary.get('replacements') or {}
                for search in replacements.keys():
                    replacement = replacements[search]
                    if not callable(replacement):
                        answerEnglish = re.sub(search, replacement, answerEnglish)
                    else:
                        answerEnglish = re.sub(search, replacement(), answerEnglish)
                answerPortuguese = ExternalAPI.translate(answerEnglish, fromLanguage='en')
                self.bot.sendMessage(chat_id=update.message.chat_id, text=(answerPortuguese or answerEnglish))
            else:
                self.logDebug(u'Friendly answer (chat_id: %s, sentence: %s, sentenceEnglish: %s, answers: None)' % (update.message.chat_id, sentence, sentenceEnglish))
                self.bot.sendMessage(chat_id=update.message.chat_id, text=random.choice(self._defaultAnswers))
