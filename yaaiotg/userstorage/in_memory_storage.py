# -*- coding: utf-8 -*-
from yaaiotg.userstorage.base import UserStorageBase, User


class InMemoryStorage(UserStorageBase):
    users: dict[int, User]

    def __init__(self):
        self.users = {}

    async def get_or_create(self, user_id: int, default: User) -> User:
        return self.users.get(user_id, default)

    async def save(self, user: User)-> None:
        self.users[user.id] = user


__author__ = 'manitou'
