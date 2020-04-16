# -*- coding: utf-8 -*-
from yaaiotg.types import Keyboard, InlineKeyboard


def make_keyboard(keys: Keyboard, cols=3):
    res = []
    for i, item in enumerate(keys):
        if not i % cols:
            res.append([])
        res[-1].append({'text': item.text})
    return res


def make_inline_keyboard(keys: InlineKeyboard, cols=3):
    res = []
    for i, item in enumerate(keys):
        if not i % cols:
            res.append([])
        res[-1].append({'text': item.text, 'callback_data': item.slug})
    return res


__author__ = 'manitou'
