# -*- coding: utf-8 -*-
from .log import debug, info, error, warning


class ObjectLog:
    def __init__(self, obj):
        self.obj = obj

    @staticmethod
    def _update_fmt(fmt):
        return '{}: ' + fmt

    def debug(self, fmt, *args, **kwargs):
        return debug(self._update_fmt(fmt), self.obj, *args, **kwargs)

    def info(self, fmt, *args, **kwargs):
        return info(self._update_fmt(fmt), self.obj, *args, **kwargs)

    def error(self, fmt, *args, **kwargs):
        return error(self._update_fmt(fmt), self.obj, *args, **kwargs)

    def warning(self, fmt, *args, **kwargs):
        return warning(self._update_fmt(fmt), self.obj, *args, **kwargs)


__author__ = 'manitou'
