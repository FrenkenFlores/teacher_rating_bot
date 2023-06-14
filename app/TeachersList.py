from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery
from BotStates import BotStates
import asyncio
import app.sql


class TeachersList:
    def __init__(self, bot: Bot, dp: Dispatcher, callback: CallbackQuery):
        self.bot = bot
        self.dp = dp
        self.callback = callback
        asyncio.create_task(BotStates.help.set())
        self.__register()

    def __register(self):
        pass

    async def answer(self):
        await self.callback.answer("List")
        teachers_dict: dict = app.sql.get_teachers_dict_from_db()
        print(teachers_dict)
        for teacher_name, answers in teachers_dict.items():
            # Calculate mean value.
            answers = [int(x) for x in answers.values()]
            mean = f"{sum(answers) / len(answers):.1f}"
            await self.callback.message.answer(f"{teacher_name}: {mean}")
        from Help import Help
        await Help(bot=self.bot, dp=self.dp, callback=self.callback).answer()
