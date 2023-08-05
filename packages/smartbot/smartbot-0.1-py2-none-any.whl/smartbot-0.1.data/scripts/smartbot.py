# coding: utf-8

import sys
import os
import argparse
import smartbot

arg_parser = argparse.ArgumentParser(description='Run smartbot')
arg_parser.add_argument('--telegram-bot-token', required=False, dest='telegram_bot_token', type=str, help='The telegram bot token (or env[TELEGRAM_BOT_TOKEN])')
arg_parser.add_argument('--slack-bot-token', required=False, dest='slack_bot_token', type=str, help='The slack bot token (or env[SLACK_BOT_TOKEN])')
arg_parser.add_argument('--wolfram-app-id', required=False, dest='wolfram_app_id', type=str, help='The wolfram app id (or env[WOLFRAM_APP_ID])')
arg_parser.add_argument('--admin-id', required=False, dest='admin_id', type=str, help='The user id to admin (or env[ADMIN_ID])')
args = arg_parser.parse_args()

telegram_token = args.telegram_bot_token or os.environ.get('TELEGRAM_BOT_TOKEN')
slack_token = args.slack_bot_token or os.environ.get('SLACK_BOT_TOKEN')
wolfram_app_id = args.wolfram_app_id or os.environ.get('WOLFRAM_APP_ID')
admin_id = args.admin_id or os.environ.get('ADMIN_ID')

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

vocabulary = {
    'aliases': {
        'standup': 'jalk',
        'diga': 'talk',
        'fale': 'talk',
        'traduz': 'translateen',
        'traduza': 'translateen',
        'nasa': 'nasa',
        'piada': 'joke',
        'manda': 'gimage',
        'quero': 'bimage'
    },
    'replacements': {
                'My creators are the company Evi \(formerly known as True Knowledge\), a semantic technology company based in Cambridge, UK': 'OLX Inc',
                'UK company': 'company',
                'Evi \(formerly known as True Knowledge\)': 'OLX Inc',
                'Stephen Wolfram': 'OLX Inc',
                '(Wolfram\|Alpha|Evi)': lambda: bot.getInfo().username
    }
}

bc = smartbot.BehaviourControl(bot)
bc.add('basic', smartbot.BasicBehaviour(bot))
bc.add('loader', smartbot.LoaderBehaviour(bot, bc))
bc.add('friendly', smartbot.FriendlyBehaviour(bot, bc, vocabulary))
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
