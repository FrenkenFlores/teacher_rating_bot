from aiogram import Dispatcher, Bot
from aiogram.types import CallbackQuery, Message

import app.sql
from app.BotStates import BotStates
import messages
import sql
import asyncio

class AddTeacher:
    """This class will represent the teacher addition process."""
    def __init__(self, bot: Bot, dp: Dispatcher, callback: CallbackQuery):
        self.bot = bot
        self.dp = dp
        self.callback = callback
        # Set the add State.
        asyncio.create_task(BotStates.add.set())
        self.__register()

    async def answer(self):
        await self.callback.answer()
        await self.callback.message.answer(messages.TYPE_TEACHER_NAME)

    async def name_handler(self, message: Message):
        name_id: str = message.text
        teachers_dict = app.sql.get_teachers_dict_from_db()
        if name_id not in teachers_dict.keys():
            sql.add_teacher_to_db(message.text)
            await message.reply(f"Added {message.text}")
        else:
            await message.reply(messages.TYPE_TEACHER_NAME_ERROR_DUPLICATE)
        from app.Help import Help
        await Help(bot=self.bot, dp=self.dp, message=message).answer()

    def __register(self):
        self.dp.register_message_handler(
            self.name_handler,
            state=BotStates.add
        )