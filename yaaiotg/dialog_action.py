# -*- coding: utf-8 -*-
import json
from aiotg import Chat
from typing import Coroutine

from yaaiotg.types import Keyboard, InlineKeyboard
from yaaiotg.userstorage.base import User
from yaaiotg.utils import make_keyboard, make_inline_keyboard


class DialogAction:
    await_answer = False

    def __init__(self, chat: Chat, user: User, message: dict = None, keyboard: Keyboard = None, inline_keyboard: InlineKeyboard = None, **keyboard_params) -> None:
        self.chat = chat
        self.user = user
        self.message = message
        self.keyboard = keyboard
        self.inline_keyboard = inline_keyboard
        self.keyboard_params = keyboard_params

    def _prepare_markup(self) -> str:
        markup = {}
        if self.keyboard:
            markup["keyboard"] = make_keyboard(self.keyboard, **self.keyboard_params)
        if self.inline_keyboard:
            markup["inline_keyboard"] = make_inline_keyboard(self.inline_keyboard, **self.keyboard_params)
        return json.dumps(markup)

    def __call__(self) -> Coroutine:
        if self.keyboard or self.inline_keyboard:
            # TODO: refactor to distinguish and not remove callbacks from subscriptions
            self.user.subscribe_for_menu(self.keyboard, self.inline_keyboard)
            return self.chat.send_text(self.message, reply_markup=self._prepare_markup())
        else:
            return self.chat.send_text(self.message)


class Say(DialogAction):
    pass


class Ask(DialogAction):
    await_answer = True


__author__ = 'manitou'
