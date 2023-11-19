# -*- coding: utf-8 -*-
from yaaiotg.types import Keyboard, InlineKeyboard


class User:
    id: int
    dialog: "Dialog | None" = None
    subscriptions: dict
    callback_subscriptions: dict

    def __init__(self, sender_data: dict) -> None:
        self.id = sender_data['id']
        self.subscriptions = {}
        self.callback_subscriptions = {}

    def subscribe_for_menu(self, keyboard: Keyboard = None, inline_keyboard: InlineKeyboard = None) -> None:
        if keyboard:
            self.subscriptions.clear()
            for key in keyboard:
                self.subscriptions[key.text] = key
        if inline_keyboard:
            for key in inline_keyboard:
                self.callback_subscriptions[key.slug] = key.callback

    def __repr__(self):
        return 'User: {}'.format(self.id)


class UserStorageBase:
    async def get_or_create(self, user_id: int, default: User = None) -> User:
        raise NotImplementedError

    async def save(self, user: User) -> None:
        raise NotImplementedError


__author__ = 'manitou'
