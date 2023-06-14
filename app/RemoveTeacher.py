import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery, Message
from app.BotStates import BotStates
import app.sql
import app.messages


class RemoveTeacher:
    def __init__(self, bot: Bot, dp: Dispatcher, callback: CallbackQuery):
        self.bot = bot
        self.dp = dp
        self.callback = callback
        asyncio.create_task(BotStates.remove.set())
        self.__register()

    async def answer(self):
        await self.callback.answer("delete")
        await self.callback.message.answer(app.messages.REMOVE_TEACHER)

    async def teacher_remove_handler(self, message: Message):
        teachers_dict = app.sql.get_teachers_dict_from_db()
        name_id: str = message.text
        if name_id in teachers_dict.keys():
            app.sql.delete_teacher_from_db(message.text)
            await message.answer(f"Deleted {message.text}")
        else:
            await message.answer(app.messages.TYPE_TEACHER_NAME_ERROR_USER_NOT_FOUND_IN_DB)
        from app.Help import Help
        await Help(bot=self.bot, dp=self.dp, message=message).answer()

    def __register(self):
        self.dp.register_message_handler(
            self.teacher_remove_handler,
            state=BotStates.remove
        )

