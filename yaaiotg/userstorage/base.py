# -*- coding: utf-8 -*-
from yaaiotg.types import Keyboard, InlineKeyboard


class User:
    id = None
    dialog = None
    subscriptions = None
    callback_subscriptions = None

    def __init__(self, sender_data):
        self.id = sender_data['id']
        self.subscriptions = {}
        self.callback_subscriptions = {}

    def subscribe_for_menu(self, keyboard: Keyboard=None, inline_keyboard: InlineKeyboard=None):
        if keyboard:
            self.subscriptions.clear()
            for key in keyboard:
                self.subscriptions[key.text] = key
        if inline_keyboard:
            self.callback_subscriptions.clear()
            for key in inline_keyboard:
                self.callback_subscriptions[key.slug] = key

    def __repr__(self):
        return 'User: {}'.format(self.id)


class UserStorageBase:
    def get_or_create(self, user_id, default=None):
        raise NotImplementedError

    def save(self, user_id, user_data):
        raise NotImplementedError


__author__ = 'manitou'
