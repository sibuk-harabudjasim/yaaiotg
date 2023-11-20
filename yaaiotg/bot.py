# -*- coding: utf-8 -*-
import logging
import traceback
from aiotg import Bot, Chat, CallbackQuery

from typing import Callable, Coroutine, Any

from yaaiotg.log.log import init as log_init
from yaaiotg.dialog import Dialog
from yaaiotg.dialog_control import DialogControl
from yaaiotg.userstorage.base import User, UserStorageBase
from yaaiotg.callback import CallbackActions


async def default_entry(dialog: Dialog, initial_message=None) -> None:
    yield dialog.say("Hi! This is test yaaiotg bot! I only can say my name.")


log = logging.getLogger()


class YaaiotgBot:
    userstorage: UserStorageBase
    bot: Bot
    entry_point: Callable[[Any], Coroutine] | None = None

    def __init__(self, *aiotg_args, userstorage: UserStorageBase, **aiotg_kwargs) -> None:
        self.userstorage = userstorage
        self.bot = Bot(*aiotg_args, **aiotg_kwargs)

    @staticmethod
    def _process_subscriptions(chat: Chat, message: dict, user: User) -> str | None:
        for key, key_info in user.subscriptions.items():
            if key == message["text"]:
                log.debug(f"Run subscriptions callback for: {key}")
                return key_info.callback(chat, message, user)

    async def _process_dialog_control(self, control: DialogControl, chat: Chat, message: dict, user: User) -> None:
        new_message = control(chat, message, user)
        if control.need_throttle:
            await self._throttle_dialog(chat, new_message or message, user)

    async def _process_callback(self, chat: Chat, callback_query: CallbackQuery, user: User) -> None:
        actions = CallbackActions(chat, callback_query, user)
        if callback := user.callback_subscriptions.get(callback_query.data, None):
            log.debug(f"Run callback for: {callback_query.data}")
            await callback(user, actions)
        callback_query.answer()

    async def _throttle_dialog(self, chat: Chat, message: dict, user: User) -> None:
        try:
            if not user.dialog:
                user.dialog = Dialog(user, self.entry_point)
            awaited_answer = await user.dialog.step(chat, message)

            log.debug(f"{awaited_answer=}, {isinstance(awaited_answer, DialogControl)=}")
            if awaited_answer and isinstance(awaited_answer, DialogControl):
                await self._process_dialog_control(awaited_answer, chat, message, user)

        except RuntimeError as e:
            # TODO: double check, if this exception is needed
            if e.__cause__ is StopIteration:
                dialog, user.dialog = user.dialog, None
                del dialog
            else:
                raise
        except Exception as e:
            # TODO: prettify
            log.error(f"generic exception caught: {e.__class__.__name__}, {str(e)}")
            traceback.print_exc()

    async def default_message_handler(self, chat: Chat, message: dict) -> None:
        user = await self.userstorage.get_or_create(chat.sender["id"], chat.sender)
        # TODO: find a way to not duplicate _throttle call
        # Can change user dialog
        message_data = self._process_subscriptions(chat, message, user)
        message = message_data or message

        # Can change user dialog
        await self._throttle_dialog(chat, message, user)
        await self.userstorage.save(user)

    async def default_callback_handler(self, chat: Chat, callback_query: CallbackQuery) -> None:
        user = await self.userstorage.get_or_create(callback_query.src["from"]["id"], callback_query.src["from"])

        await self._process_callback(chat, callback_query, user)
        await self.userstorage.save(user)

    async def run(self):
        log_init()
        if not self.entry_point:
            self.entry_point = default_entry
        self.bot.default(self.default_message_handler)
        self.bot.callback(self.default_callback_handler)
        await self.bot.loop()


__author__ = 'manitou'
