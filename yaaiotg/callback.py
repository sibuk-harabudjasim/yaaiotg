from aiotg import Chat, CallbackQuery

from yaaiotg.utils import make_inline_keyboard
from yaaiotg.types import InlineKeyboard
from yaaiotg.userstorage.base import User


class CallbackActions:
    def __init__(self, chat: Chat, callback_query: CallbackQuery, user: User) -> None:
        self.chat = chat
        self.callback_query = callback_query
        self.user = user

    def answer(self) -> None:
        self.callback_query.answer()

    def _prepare_markup(self, markup: InlineKeyboard) -> str:
        return {
           "inline_keyboard": make_inline_keyboard(markup),
        }

    def edit_message(self, new_text, reply_markup: InlineKeyboard | None = None) -> None:
        if reply_markup:
            markup = self._prepare_markup(reply_markup)
            self.user.subscribe_for_menu(inline_keyboard=reply_markup)
            self.chat.edit_text(self.callback_query.src["message"]["message_id"], new_text, markup=markup)

    def edit_markup(self, new_markup: InlineKeyboard) -> None:
        self.user.subscribe_for_menu(inline_keyboard=new_markup)
        self.chat.edit_reply_markup(self.callback_query.src["message"]["message_id"], markup=self._prepare_markup(new_markup))

    def delete_message(self) -> None:
        self.chat.delete_message(self.callback_query.src["message"]["message_id"])
