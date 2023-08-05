#!/usr/bin/env python2.7
# coding: utf-8

import sys
import os
import argparse
import smartbot

arg_parser = argparse.ArgumentParser(description='Run smartbot')
arg_parser.add_argument('--telegram-bot-token', required=False, dest='telegram_bot_token', type=str, help='The telegram bot token (or env[SMARTBOT_TELEGRAM_TOKEN])')
arg_parser.add_argument('--slack-bot-token', required=False, dest='slack_bot_token', type=str, help='The slack bot token (or env[SMARTBOT_SLACK_TOKEN])')
arg_parser.add_argument('--wolfram-app-id', required=False, dest='wolfram_app_id', type=str, help='The wolfram app id (or env[SMARTBOT_WOLFRAM_APPID])')
arg_parser.add_argument('--admin-id', required=False, dest='admin_id', type=str, help='The user id to admin (or env[SMARTBOT_ADMIN_ID])')
arg_parser.add_argument('--config', required=False, dest='config', type=str, help='The configuration file (or env[SMARTBOT_CONFIG])')
args = arg_parser.parse_args()

telegram_token = args.telegram_bot_token or os.environ.get('SMARTBOT_TELEGRAM_TOKEN')
slack_token = args.slack_bot_token or os.environ.get('SMARTBOT_SLACK_TOKEN')
wolfram_app_id = args.wolfram_app_id or os.environ.get('SMARTBOT_WOLFRAM_APPID')
admin_id = args.admin_id or os.environ.get('SMARTBOT_ADMIN_ID')
config = args.config or os.environ.get('SMARTBOT_CONFIG')

if telegram_token and slack_token:
    sys.stderr.write('There are already telegram and slack token set. Please choose only one (see --help for details).\n')
    exit(0)

if telegram_token:
    bot = smartbot.TelegramBot(telegram_token, admin_id)
elif slack_token:
    bot = smartbot.SlackBot(slack_token, admin_id)
else:
    sys.stderr.write('Please set the telegram/slack token (see --help for details).\n')
    exit(0)

if config and os.path.exists(config):
    bot.setConfigFile(config)
elif config and not os.path.exists(config):
    smartbot.Utils.logWarning(bot, 'MAIN', 'The configuration file does not exist. Assuming default configuration')
else:
    smartbot.Utils.logWarning(bot, 'MAIN', 'There is no config file set. Using default configuration')

bc = smartbot.BehaviourControl(bot)
bc.add('basic', smartbot.BasicBehaviour(bot))
bc.add('loader', smartbot.LoaderBehaviour(bot, bc))
bc.add('friendly', smartbot.FriendlyBehaviour(bot, bc))
bc.add('translate', smartbot.TranslateBehaviour(bot))
bc.add('joke', smartbot.JokeBehaviour(bot))
bc.add('google_image', smartbot.GoogleImageBehaviour(bot))
bc.add('bing_image', smartbot.BingImageBehaviour(bot))
bc.add('nasa', smartbot.NasaBehaviour(bot))
bc.add('talk', smartbot.TalkBehaviour(bot))
bc.add('wolfram', smartbot.WolframBehaviour(bot, wolfram_app_id))
bc.add('evi', smartbot.EviBehaviour(bot))
bc.load('basic')
bc.load('loader')
bc.load('friendly')
bc.load('translate')
bc.load('joke')
bc.load('google_image')
bc.load('bing_image')
bc.load('nasa')
bc.load('talk')
bc.load('wolfram')
bc.load('evi')

smartbot.Utils.logInfo(bot, 'MAIN', 'Starting bot')

bot.listen()
