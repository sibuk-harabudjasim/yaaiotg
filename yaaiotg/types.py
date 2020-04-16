# -*- coding: utf-8 -*-
from typing import List, Callable, Any

from attr.__init__ import dataclass


@dataclass(order=True)
class KbdKey:
    text: str
    callback: Callable[..., Any] = lambda chat, message, user: message['text']


@dataclass(order=True)
class KbdInlineKey:
    text: str
    slug: str
    callback: Callable[..., Any]


Keyboard = List[KbdKey]
InlineKeyboard = List[KbdInlineKey]

__author__ = 'manitou'
