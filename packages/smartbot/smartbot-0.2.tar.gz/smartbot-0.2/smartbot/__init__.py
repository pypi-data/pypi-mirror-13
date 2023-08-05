#!/usr/bin/env python
# The MIT License (MIT)
#
# Copyright (c) 2015 Pedro Henrique Marques Lira
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""A library to build an enhanced bot to telegram and slack"""

__author__ = 'pedrohml@gmail.com'
__version__ = '0.2'

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
