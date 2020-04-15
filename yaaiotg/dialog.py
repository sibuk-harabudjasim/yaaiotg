# -*- coding: utf-8 -*-
import inspect

from yaaiotg.dialog_action import Say, Ask, DialogAction


class Dialog:
    agen = None
    _chat = None

    class DialogActions:
        def __init__(self, dialog):
            self.dialog = dialog

        def say(self, *args, **kwargs):
            return self.dialog.say(*args, **kwargs)

        def ask(self, *args, **kwargs):
            return self.dialog.ask(*args, **kwargs)

    def __init__(self, chat):
        self._chat = chat

    def say(self, message):
        return Say(self._chat, message)

    def ask(self, message):
        return Ask(self._chat, message)

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

    async def start(self, func):
        self.agen = func(self.DialogActions(self))
        if not inspect.isasyncgen(self.agen):
            raise Exception('scenario function is not generator')
        return await self._throttle()

    async def resume(self, chat, message):
        self._chat = chat
        return await self._throttle(message)


__author__ = 'manitou'
