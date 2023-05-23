from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import Dispatcher
import messages

class StartKeyboard:
    def __init__(self, dp: Dispatcher):
        self.keyboard = InlineKeyboardMarkup()
        self.button_rate_teacher = InlineKeyboardButton(text=messages.BUTTON_RATE_TEACHER, callback_data="rate_teacher")
        self.button_add_teacher = InlineKeyboardButton(text=messages.BUTTON_ADD_TEACHER, callback_data="add_teacher")
        self.keyboard.add(self.button_add_teacher, self.button_rate_teacher)

        @dp.callback_query_handler(text="add_teacher")
        async def add_teacher(callback: CallbackQuery):
            await callback.answer(text="Add")

        @dp.callback_query_handler(text="rate_teacher")
        async def add_teacher(callback: CallbackQuery):
            await callback.answer(text="Rate")
