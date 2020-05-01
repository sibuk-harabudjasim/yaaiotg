# -*- coding: utf-8 -*-
import traceback

from aiotg import Bot

from yaaiotg.dialog import Dialog
from yaaiotg.userstorage.base import User


async def default_entry(dialog, initial_message=None):
    yield dialog.say('Hi! This is test yaaiotg bot! I only can say my name.')


class YaaiotgBot:
    userstorage = None
    user_class = None
    bot = None

    entry_point = None
    default_subscriptions = None

    def __init__(self, *args, userstorage, user_class=User, **kwargs):
        self.userstorage = userstorage
        self.user_class = user_class
        self.bot = Bot(*args, **kwargs)

    @staticmethod
    def _process_subscriptions(chat, message, user):
        for key, key_info in user.subscriptions.items():
            if key == message['text']:
                return key_info.callback(chat, message, user)

    async def _throttle_dialog(self, chat, message, user):
        try:
            if not user.dialog:
                user.dialog = Dialog(user, self.entry_point)
            awaited_answer = await user.dialog.step(chat, message)

            if not awaited_answer:
                dialog, user.dialog = user.dialog, None
                del dialog

        except RuntimeError as e:
            # TODO: double check, if this exception is needed
            if e.__cause__ is StopIteration:
                dialog, user.dialog = user.dialog, None
                del dialog
            else:
                raise
        except Exception as e:
            # TODO: prettify
            print('generic exception caught:', e.__class__.__name__, str(e))
            traceback.print_exc()

    async def default_message_handler(self, chat, message):
        user = self.userstorage.get_or_create(chat.sender['id'], self.user_class(chat.sender))
        # Can change user dialog
        message_data = self._process_subscriptions(chat, message, user)
        message = message_data or message

        # Can change user dialog
        self._throttle_dialog(chat, message, user)
        self.userstorage.save(chat.sender['id'], user)

    async def default_callback_handler(self, chat, callback_query):
        user = self.userstorage.get_or_create(chat.sender['id'], self.user_class(chat.sender))
        # do smth
        self.userstorage.save(chat.sender['id'], user)

    def run(self, *args, **kwargs):
        if not self.entry_point:
            self.entry_point = default_entry
        self.bot.default(self.default_message_handler)
        self.bot.callback(self.default_callback_handler)
        self.bot.run(*args, **kwargs)


__author__ = 'manitou'
