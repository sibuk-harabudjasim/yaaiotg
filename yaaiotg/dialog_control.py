# -*- coding: utf-8 -*-


class DialogControl:
    need_throttle = True

    def __call__(self, chat, message, user):
        raise NotImplementedError

    def __repr__(self):
        return 'Control({})'.format(self.__class__.__name__)


class EndDialog(DialogControl):
    need_throttle = False

    def __call__(self, chat, message, user):
        user.dialog, dialog = None, user.dialog
        del dialog


class SubDialogRun(DialogControl):
    def __init__(self, scenario, initial_message=None):
        self.scenario = scenario
        self.initial_message = initial_message

    def __call__(self, chat, message, user):
        from yaaiotg.dialog import SubDialog
        new_dialog = SubDialog(user, self.scenario, user.dialog)
        user.dialog = new_dialog
        return self.initial_message

    def __repr__(self):
        return '{} scenario: {}, message: {}'.format(super().__repr__(), self.scenario.__name__, self.initial_message)


class SubDialogReturn(DialogControl):
    def __init__(self, parent_dialog, return_result):
        self.parent = parent_dialog
        self.result = return_result

    def __call__(self, chat, message, user):
        user.dialog, dialog = self.parent, user.dialog
        del dialog
        return self.result

    def __repr__(self):
        return '{} with result: {}'.format(super().__repr__(), self.result)


class NewDialog(DialogControl):
    def __init__(self, scenario):
        self.scenario = scenario

    def __call__(self, chat, message, user):
        from yaaiotg.dialog import Dialog
        new_dialog = Dialog(user, self.scenario)
        user.dialog, old_dialog = new_dialog, user.dialog
        del old_dialog

    def __repr__(self):
        return '{} scenario: {}'.format(super().__repr__(), self.scenario.__name__)


__author__ = 'manitou'
