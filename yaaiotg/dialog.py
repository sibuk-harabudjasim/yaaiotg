# -*- coding: utf-8 -*-
import inspect
import logging
from typing import Callable, Coroutine, Any
from aiotg import Chat

from yaaiotg.casts import as_text, as_is
from yaaiotg.types import Keyboard, InlineKeyboard
from yaaiotg.userstorage.base import User
from yaaiotg.dialog_action import Say, Ask, DialogAction
from yaaiotg.dialog_control import DialogControl, EndDialog, SubDialogReturn, SubDialogRun


log = logging.getLogger()
default_message_cast = as_text
Scenario = Callable[["Dialog", str | None], Coroutine]


class DialogActions:
    def __init__(self, dialog: "Dialog"):
        self.dialog = dialog
        self.user = dialog.user

    def say(self, message: dict, keyboard: Keyboard = None, inline_keyboard: InlineKeyboard = None, **keyboard_params):
        return self.dialog.say(message, keyboard, inline_keyboard, **keyboard_params)

    def ask(self, message: dict, cast: Callable = None, keyboard: Keyboard = None, inline_keyboard: InlineKeyboard = None, **keyboard_params):
        return self.dialog.ask(message, cast, keyboard, inline_keyboard, **keyboard_params)

    def subdialog(self, scenario: Scenario, initial_message: str = None):
        return self.dialog.subdialog(scenario, initial_message)

    def end(self):
        return self.dialog.end()


class SubDialogActions(DialogActions):
    def return_(self, value: Any):
        return self.dialog.return_(value)


class GeneratorWrapper:
    def __init__(self, gen: Scenario):
        self.gen = gen
        if not inspect.isasyncgen(self.gen) and not inspect.isgenerator(self.gen):
            raise Exception("scenario function is not generator")
        if inspect.isasyncgen(self.gen):
            self.next = self.gen.__anext__
            self.send = self.gen.asend

    async def next(self):
        return self.gen.__next__()

    async def send(self, value: Any):
        return self.gen.send(value)


async def async_wrapper(gen: Callable):
    for val in gen():
        yield val


class Dialog:
    agen: GeneratorWrapper | None = None
    _chat: Chat | None = None
    user: User
    scenario: Scenario
    dialog_actions_class: type = DialogActions
    message_cast: Callable

    def __init__(self, user, scenario):
        self.user = user
        self.scenario = scenario
        # TODO: find better way to cast incoming messages
        self.message_cast = default_message_cast

    def say(self, message: dict, keyboard: Keyboard = None, inline_keyboard: InlineKeyboard = None, **keyboard_params):
        return Say(self._chat, self.user, message, keyboard=keyboard, inline_keyboard=inline_keyboard, **keyboard_params)

    def ask(self, message: dict, cast: Callable = None, keyboard: Keyboard = None, inline_keyboard: InlineKeyboard = None, **keyboard_params):
        if cast:
            self.message_cast = cast
        return Ask(self._chat, self.user, message, keyboard=keyboard, inline_keyboard=inline_keyboard, **keyboard_params)

    def subdialog(self, scenario: Scenario, initial_message: str = None):
        self.message_cast = as_is
        return SubDialogRun(scenario, initial_message)

    @staticmethod
    def end():
        return EndDialog()

    # FIXME: change message to incoming, to distinguish flow direction in functions
    def _get_action(self, message: Any = None):
        if message:
            cast, self.message_cast = self.message_cast, default_message_cast
            return self.agen.send(cast(message))
        return self.agen.next()

    async def _throttle(self, message: Any = None):
        log.debug("Throttling")
        while 1:
            try:
                action = await self._get_action(message)
            except (StopIteration, StopAsyncIteration) as e:
                log.debug(f"StopIteration: {str(e)}")
                return EndDialog(user_initiated=False)
            message = None
            if isinstance(action, DialogAction):
                await action()
                if action.await_answer:
                    return
            elif inspect.isawaitable(action):
                await action
            elif isinstance(action, DialogControl):
                return action

    async def step(self, chat: Chat, message: Any):
        self._chat = chat
        if not self.agen:
            self.agen = GeneratorWrapper(self.scenario(
                self.dialog_actions_class(self), self.message_cast(message)))
            self.message_cast = default_message_cast
            message = None
        ret = await self._throttle(message)
        log.debug(f"Throttle result: {ret or 'Regular await'}")
        return ret

    def __repr__(self):
        return f"{self.user} Dialog: {self.scenario.__name__}"


class SubDialog(Dialog):
    dialog_actions_class: type = SubDialogActions

    def __init__(self, user: User, scenario: Scenario, parent_dialog: Dialog):
        super().__init__(user, scenario)
        self.parent = parent_dialog

    def return_(self, value: Any):
        return SubDialogReturn(self.parent, value)

    async def step(self, chat: Chat, message: Any):
        ret = await super().step(chat, message)
        if isinstance(ret, EndDialog) and not ret.user_initiated:
            log.warning('End of subdialog without return. '
                        'Empty result won\'t be passed to parent dialog. '
                        'If it\'s OK, just ignore this warning.')
            ret = SubDialogReturn(self.parent, None)
            ret.need_throttle = False
        return ret


__author__ = 'manitou'
