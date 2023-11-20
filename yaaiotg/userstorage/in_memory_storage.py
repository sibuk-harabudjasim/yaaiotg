# -*- coding: utf-8 -*-
from yaaiotg.userstorage.base import UserStorageBase, User


class InMemoryStorage(UserStorageBase):
    users: dict[int, User]

    def __init__(self):
        self.users = {}

    async def get_or_create(self, user_id: int, user_meta: dict | None = None) -> User:
        if user_id not in self.users:
            self.users[user_id] = User(user_id, user_meta)
        return self.users[user_id]

    async def save(self, user: User)-> None:
        self.users[user.id] = user


__author__ = 'manitou'
