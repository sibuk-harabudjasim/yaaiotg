# -*- coding: utf-8 -*-


class User:
    dialog = None
    permanent_subscriptions = None
    subscriptions = None

    def __init__(self, *args, **kwargs):
        self.permanent_subscriptions = {}
        self.subscriptions = {}


class UserStorageBase:
    def get_or_create(self, user_id, default=None):
        raise NotImplementedError

    def save(self, user_id, user_data):
        raise NotImplementedError


__author__ = 'manitou'
