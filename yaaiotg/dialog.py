# -*- coding: utf-8 -*-
import inspect

from yaaiotg.casts import as_text, as_is
from yaaiotg.dialog_action import Say, Ask, DialogAction
from yaaiotg.dialog_control import DialogControl, EndDialog, SubDialogReturn, SubDialogRun
from yaaiotg.log.object_log import ObjectLog

default_message_cast = as_text


class DialogActions:
    def __init__(self, dialog):
        self.dialog = dialog

    def say(self, *args, **kwargs):
        return self.dialog.say(*args, **kwargs)

    def ask(self, *args, **kwargs):
        return self.dialog.ask(*args, **kwargs)

    def subdialog(self, *args, **kwargs):
        return self.dialog.subdialog(*args, **kwargs)

    def end(self):
        return self.dialog.end()


class SubDialogActions(DialogActions):
    def return_(self, *args, **kwargs):
        return self.dialog.return_(*args, **kwargs)


class Dialog:
    agen = None
    _chat = None
    user = None
    scenario = None
    dialog_actions_class = DialogActions
    log = None

    def __init__(self, user, scenario):
        self.user = user
        self.scenario = scenario
        self.message_cast = default_message_cast
        self.log = ObjectLog(self)

    def say(self, message, **kwargs):
        return Say(self._chat, self.user, message, **kwargs)

    def ask(self, message=None, cast=None):
        if cast:
            self.message_cast = cast
        return Ask(self._chat, self.user, message)

    def subdialog(self, scenario, initial_message=None):
        self.message_cast = as_is
        return SubDialogRun(scenario, initial_message)

    @staticmethod
    def end():
        return EndDialog()

    def _get_action(self, message=None):
        if message:
            cast, self.message_cast = self.message_cast, default_message_cast
            return self.agen.asend(cast(message))
        return self.agen.__anext__()

    async def _throttle(self, message=None):
        self.log.debug('Throttling')
        while 1:
            try:
                action = await self._get_action(message)
            except (StopIteration, StopAsyncIteration) as e:
                self.log.debug('StopIteration: {}', e)
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

    async def step(self, chat, message):
        self._chat = chat
        if not self.agen:
            self.agen = self.scenario(self.dialog_actions_class(self), self.message_cast(message))
            self.message_cast = default_message_cast
            message = None
            if not inspect.isasyncgen(self.agen):
                raise Exception('scenario function is not generator')
        ret = await self._throttle(message)
        self.log.debug('Throttle result: {}', ret or 'Regular await')
        return ret

    def __repr__(self):
        return '{} Dialog: {}'.format(self.user, self.scenario.__name__)


class SubDialog(Dialog):
    dialog_actions_class = SubDialogActions

    def __init__(self, user, scenario, parent_dialog):
        super().__init__(user, scenario)
        self.parent = parent_dialog

    def return_(self, value):
        return SubDialogReturn(self.parent, value)

    async def step(self, chat, message):
        ret = await super().step(chat, message)
        if isinstance(ret, EndDialog) and not ret.user_initiated:
            self.log.warning('End of subdialog without return. '
                             'Empty result won\'t be passed to parent dialog. '
                             'If it\'s OK, just ignore this warning.')
            ret = SubDialogReturn(self.parent, None)
            ret.need_throttle = False
        return ret


__author__ = 'manitou'
