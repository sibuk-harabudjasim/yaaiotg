# -*- coding: utf-8 -*-
from aiotg import Chat
from typing import Callable, Coroutine, Any

from yaaiotg.casts import as_is
from yaaiotg.userstorage.base import User

class DialogControl:
    need_throttle = True

    def __call__(self, chat: Chat, message: dict, user: User):
        raise NotImplementedError

    def __repr__(self):
        return f"Control({self.__class__.__name__})"


class EndDialog(DialogControl):
    need_throttle = False
    user_initiated = None

    def __init__(self, user_initiated: bool = True) -> None:
        self.user_initiated = user_initiated

    def __call__(self, chat: Chat, message: dict, user: User):
        user.dialog, dialog = None, user.dialog
        del dialog

    def __repr__(self):
        return f"{super().__repr__()}{' user initiated' if self.user_initiated else ''}"


class SubDialogRun(DialogControl):
    def __init__(self, scenario: Callable[[Any], Coroutine], initial_message: str | None = None):
        self.scenario = scenario
        self.initial_message = initial_message

    def __call__(self, chat: Chat, message: dict, user: User) -> str | None:
        from yaaiotg.dialog import SubDialog
        new_dialog = SubDialog(user, self.scenario, user.dialog)
        user.dialog = new_dialog
        if self.initial_message:
            user.dialog.message_cast = as_is
        return self.initial_message

    def __repr__(self):
        return f"{super().__repr__()} scenario: {self.scenario.__name__}, message: {self.initial_message}"


class SubDialogReturn(DialogControl):
    def __init__(self, parent_dialog: "Dialog", return_result: Any) -> None:
        self.parent = parent_dialog
        self.result = return_result

    def __call__(self, chat: Chat, message: dict, user: User) -> Any:
        user.dialog, dialog = self.parent, user.dialog
        del dialog
        if self.result:
            user.dialog.message_cast = as_is
        return self.result

    def __repr__(self):
        return f"{super().__repr__()} with result: {self.result}"


class NewDialog(DialogControl):
    def __init__(self, scenario):
        self.scenario = scenario

    def __call__(self, chat, message, user):
        from yaaiotg.dialog import Dialog
        new_dialog = Dialog(user, self.scenario)
        user.dialog, old_dialog = new_dialog, user.dialog
        del old_dialog

    def __repr__(self):
        return f"{super().__repr__()} scenario: {self.scenario.__name__}"


__author__ = 'manitou'
