# -*- coding: utf-8 -*-
import inspect
from typing import Callable, Any

from yaaiotg.dialog_action import Say, Ask, DialogAction


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

    def say(self, message, **kwargs):
        return Say(self._chat, self.user, message, **kwargs)

    def ask(self, message=None):
        return Ask(self._chat, self.user, message)

    def _get_action(self, message=None):
        if message:
            return self.agen.asend(message)
        return self.agen.__anext__()

    async def _throttle(self, message=None):
        while 1:
            try:
                action = await self._get_action(message)
            except StopIteration:
                return
            except StopAsyncIteration:
                return
            message = None
            if isinstance(action, DialogAction):
                await action()
                if action.await_answer:
                    return self.agen
            elif inspect.isawaitable(action):
                await action

    async def step(self, chat, message):
        self._chat = chat
        if not self.agen:
            self.agen = self.scenario(self.DialogActions(self), message)
            message = None
            if not inspect.isasyncgen(self.agen):
                raise Exception('scenario function is not generator')
        return await self._throttle(message)


class SubAction:
    def __call__(self, chat, message, user):
        raise NotImplementedError


class NewDialog(SubAction):
    def __init__(self, scenario: Callable[[Dialog.DialogActions], Any]):
        self.scenario = scenario

    def __call__(self, chat, message, user):
        return Dialog(user, self.scenario)


__author__ = 'manitou'
