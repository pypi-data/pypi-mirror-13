# coding: utf-8

import sys
import time
import logging
import requests
from lxml import html

class Utils:
    logger = None
    debug = False
    debugOutput = None

    @staticmethod
    def _getLogger():
        if not Utils.logger:
            logger = logging.getLogger('smartbot')
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s %(levelname)s (%(botname)s) %(classname)s - %(message)s')
            streamHandler = logging.StreamHandler(sys.stdout)
            streamHandler.setLevel(logging.DEBUG)
            streamHandler.setFormatter(formatter)
            logger.addHandler(streamHandler)
            fileHandler = logging.FileHandler('smartbot.log')
            fileHandler.setLevel(logging.DEBUG)
            fileHandler.setFormatter(formatter)
            logger.addHandler(fileHandler)
            Utils.logger = logger
        return Utils.logger

    @staticmethod
    def _getLogArgs(bot, className):
        botInfo = bot.getInfo()
        return { 'botname': botInfo.username, 'classname': className }

    @staticmethod
    def crawlUrl(url):
        response = requests.get(url)
        return html.fromstring(response.content)

    @staticmethod
    def logDebug(bot, className, message):
        Utils._getLogger().debug(message, extra=Utils._getLogArgs(bot, className))

    @staticmethod
    def logInfo(bot, className, message):
        Utils._getLogger().info(message, extra=Utils._getLogArgs(bot, className))

    @staticmethod
    def logWarning(bot, className, message):
        Utils._getLogger().warning(message, extra=Utils._getLogArgs(bot, className))

    @staticmethod
    def logError(bot, className, message):
        Utils._getLogger().error(message, extra=Utils._getLogArgs(bot, className))
