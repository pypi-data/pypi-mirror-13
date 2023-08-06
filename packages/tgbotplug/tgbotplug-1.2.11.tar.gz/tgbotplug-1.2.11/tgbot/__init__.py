#!/usr/bin/env python
# coding=utf-8

__version__ = '1.2.11'

from .pluginbase import TGPluginBase, TGCommandBase
from .tgbot import TGBot

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
