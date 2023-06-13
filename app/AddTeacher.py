from aiogram import Dispatcher
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
import json
import messages


class AddTeacher:
    """This class will represent the teacher addition process."""
    def __init__(self, odp: Dispatcher, callback: CallbackQuery):
        self.odp = odp
        self.callback = callback

    async def answer(self):
        await self.callback.answer()
        await self.callback.message.answer(messages.TYPE_TEACHER_NAME)

