# -*- coding: utf-8 -*-
import inspect

from yaaiotg.casts import as_text
from yaaiotg.dialog_action import Say, Ask, DialogAction
from yaaiotg.dialog_control import DialogControl, EndDialog

default_message_cast = as_text


class Dialog:
    agen = None
    _chat = None
    user = None
    scenario = None

    class DialogActions:
        def __init__(self, dialog):
            self.dialog = dialog

        def say(self, *args, **kwargs):
            return self.dialog.say(*args, **kwargs)

        def ask(self, *args, **kwargs):
            return self.dialog.ask(*args, **kwargs)

    def __init__(self, user, scenario):
        self.user = user
        self.scenario = scenario
        self.message_cast = default_message_cast

    def say(self, message, **kwargs):
        return Say(self._chat, self.user, message, **kwargs)

    def ask(self, message=None, cast=None):
        if cast:
            self.message_cast = cast
        return Ask(self._chat, self.user, message)

    def _get_action(self, message=None):
        if message:
            cast, self.message_cast = self.message_cast, default_message_cast
            return self.agen.asend(cast(message))
        return self.agen.__anext__()

    async def _throttle(self, message=None):
        while 1:
            try:
                action = await self._get_action(message)
            except (StopIteration, StopAsyncIteration):
                return EndDialog()
            message = None
            if isinstance(action, DialogAction):
                await action()
                if action.await_answer:
                    return
            elif inspect.isawaitable(action):
                await action
            elif isinstance(action, DialogControl):
                return action

    async def step(self, chat, message):
        self._chat = chat
        if not self.agen:
            self.agen = self.scenario(self.DialogActions(self), default_message_cast(message))
            message = None
            if not inspect.isasyncgen(self.agen):
                raise Exception('scenario function is not generator')
        return await self._throttle(message)


__author__ = 'manitou'
