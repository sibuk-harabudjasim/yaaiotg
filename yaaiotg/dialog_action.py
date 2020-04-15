# -*- coding: utf-8 -*-


class DialogAction:
    await_answer = False

    def __init__(self, chat):
        self.chat = chat

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


class Ask(DialogAction):
    await_answer = True

    def __init__(self, chat, message):
        super().__init__(chat)
        self.message = message

    async def __call__(self):
        return self.chat.send_text(self.message)


class Say(DialogAction):
    def __init__(self, chat, message):
        super().__init__(chat)
        self.message = message

    async def __call__(self):
        return self.chat.send_text(self.message)


__author__ = 'manitou'
