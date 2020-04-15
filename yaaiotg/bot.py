# -*- coding: utf-8 -*-
import traceback

from aiotg import Bot

from yaaiotg.dialog import Dialog
from yaaiotg.userstorage.base import User


async def default_entry(dialog, initial_message=None):
    yield dialog.say('Hi! This is test yaaoitg bot! I only can say my name.')


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

    async def default_handler(self, chat, message):
        user = self.userstorage.get_or_create(chat.sender['id'], self.user_class(chat.sender))
        try:
            if user.dialog:
                awaited_answer = await user.dialog.resume(chat, message['text'])
            else:
                user.dialog = Dialog(chat)
                awaited_answer = await user.dialog.start(self.entry_point)
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
        self.userstorage.save(chat.sender['id'], user)

    def run(self, *args, **kwargs):
        if not self.entry_point:
            self.entry_point = default_entry
        self.bot.default(self.default_handler)
        self.bot.run(*args, **kwargs)


__author__ = 'manitou'
