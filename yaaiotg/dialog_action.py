# -*- coding: utf-8 -*-
import json

from yaaiotg.utils import make_keyboard, make_inline_keyboard


class DialogAction:
    await_answer = False

    def __init__(self, chat, user, message=None):
        self.chat = chat
        self.user = user
        self.message = message

    async def __call__(self):
        raise NotImplementedError


class Ask(DialogAction):
    await_answer = True

    async def __call__(self):
        if self.message:
            return self.chat.send_text(self.message)


class Say(DialogAction):
    def __init__(self, chat, user, message, keyboard=None, inline_keyboard=None, **kwargs):
        super().__init__(chat, user, message)
        self.keyboard = keyboard
        self.inline_keyboard = inline_keyboard
        self.kwargs = kwargs

    def _prepare_markup(self):
        markup = {}
        if self.keyboard:
            markup['keyboard'] = make_keyboard(self.keyboard, **self.kwargs)
        if self.inline_keyboard:
            markup['inline_keyboard'] = make_inline_keyboard(self.inline_keyboard, **self.kwargs)
        return json.dumps(markup)

    async def __call__(self):
        if self.keyboard or self.inline_keyboard:
            self.user.subscribe_for_menu(self.keyboard, self.inline_keyboard)
            return self.chat.send_text(self.message, reply_markup=self._prepare_markup())
        return self.chat.send_text(self.message)


__author__ = 'manitou'
