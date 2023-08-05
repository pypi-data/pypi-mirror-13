#!/usr/bin/env python

"""A library to build an enhanced bot to telegram and slack"""

__author__ = 'pedrohml@gmail.com'
__version__ = '0.1'

from .utils import Utils
from .external_api import ExternalAPI

from .bot import Bot
from .telegram_bot import TelegramBot
from .slack_bot import SlackBot

from .behaviour_control import BehaviourControl
from .behaviour import Behaviour
from .basic_behaviour import BasicBehaviour
from .loader_behaviour import LoaderBehaviour
from .google_image_behaviour import GoogleImageBehaviour
from .bing_image_behaviour import BingImageBehaviour
from .translate_behaviour import TranslateBehaviour
from .joke_behaviour import JokeBehaviour
from .nasa_behaviour import NasaBehaviour
from .friendly_behaviour import FriendlyBehaviour
from .talk_behaviour import TalkBehaviour
from .wolfram_behaviour import WolframBehaviour
from .evi_behaviour import EviBehaviour

__all__ = ['Utils', 'ExternalAPI', 'Bot', 'TelegramBot', 'SlackBot', 'BehaviourControl', 'Behaviour',
'BasicBehaviour', 'LoaderBehaviour', 'GoogleImageBehaviour', 'BingImageBehaviour', 'TranslateBehaviour',
'JokeBehaviour', 'NasaBehaviour', 'FriendlyBehaviour', 'TalkBehaviour', 'WolframBehaviour', 'EviBehaviour']
