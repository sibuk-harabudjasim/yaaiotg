# -*- coding: utf-8 -*-
from yaaiotg.userstorage.base import UserStorageBase


class InMemoryStorage(UserStorageBase):
    users = None

    def __init__(self):
        self.users = {}

    def get_or_create(self, user_id, default=None):
        return self.users.get(user_id, default)

    def save(self, user_id, user_data):
        self.users[user_id] = user_data


__author__ = 'manitou'
