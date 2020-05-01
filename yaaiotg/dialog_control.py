# -*- coding: utf-8 -*-


class DialogControl:
    need_throttle = True

    def __call__(self, chat, message, user):
        raise NotImplementedError


class EndDialog(DialogControl):
    need_throttle = False

    def __call__(self, chat, message, user):
        user.dialog, dialog = None, user.dialog
        del dialog


class NewDialog(DialogControl):
    def __init__(self, scenario):
        self.scenario = scenario

    def __call__(self, chat, message, user):
        from yaaiotg.dialog import Dialog
        new_dialog = Dialog(user, self.scenario)
        user.dialog, old_dialog = new_dialog, user.dialog
        del old_dialog


__author__ = 'manitou'
