import itertools

from aiogram import Dispatcher, Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.callback_data import CallbackData
import json
import messages
from BotStates import BotStates
import asyncio
import app.sql

QUESTIONS_PATH = "questions.json"


class RateTeacherQuestion:
    """This class will represent the rating process."""
    def __init__(self, bot: Bot, dp: Dispatcher, callback: CallbackQuery):
        """__init__ will take two arguments, the current Dispatcher and the first callback that was
        received from the caller function. __init__ will initialize the score keyboard and the
        generator of the questions."""
        self.cb_score_filter = CallbackData("rate", "score")
        # Add inline keyboard with the buttons that represent the score.
        self.inline_rate_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="1", callback_data=self.cb_score_filter.new("1")),
                    InlineKeyboardButton(text="2", callback_data=self.cb_score_filter.new("2")),
                    InlineKeyboardButton(text="3", callback_data=self.cb_score_filter.new("3")),
                    InlineKeyboardButton(text="4", callback_data=self.cb_score_filter.new("4")),
                    InlineKeyboardButton(text="5", callback_data=self.cb_score_filter.new("5"))
                ],
                [
                    InlineKeyboardButton(text="6", callback_data=self.cb_score_filter.new("6")),
                    InlineKeyboardButton(text="7", callback_data=self.cb_score_filter.new("7")),
                    InlineKeyboardButton(text="8", callback_data=self.cb_score_filter.new("8")),
                    InlineKeyboardButton(text="9", callback_data=self.cb_score_filter.new("9")),
                    InlineKeyboardButton(text="10", callback_data=self.cb_score_filter.new("10"))
                ]
            ]
        )
        self.bot = bot
        # Set the current Dispatcher.
        self.dp = dp
        # Set the first callback.
        self.callback = callback
        asyncio.create_task(BotStates.rate.set())
        # Init the generator of the questions.
        self.questions = self.get_question()
        # Scores list.
        self.scores = []
        # Teacher name_id.
        self.name_id = str()
        self.__register()


    async def rate_teacher_callback_handler(self, callback: CallbackQuery):
        self.callback = callback
        await self.answer()

    async def teacher_name_callback_handler(self, message: Message):
        teachers_dict: dict = app.sql.get_teachers_dict_from_db()
        if message.text in teachers_dict:
            self.name_id = message.text
            await message.reply(text=messages.SELECT_SCORE)
            question = next(self.questions)
            await message.answer(text=question, reply_markup=self.inline_rate_keyboard)
        else:
            await message.reply(messages.TYPE_TEACHER_NAME_ERROR_USER_NOT_FOUND_IN_DB)
            from Help import Help
            await Help(bot=self.bot, dp=self.dp, callback=self.callback).answer()

    def get_question(self):
        """This is a generator function, it will return the next question after receiving callback query from
        the rating inline keyboard."""
        # Open the json file that contains questions.
        with open(QUESTIONS_PATH, "r") as json_questions:
            questions: dict = json.load(json_questions)
        if not questions:
            raise FileNotFoundError
        for q in questions.values():
            yield q

    def reset_generator(self):
        self.questions = itertools.islice(iter(self.get_question()), 0, None)


    async def answer(self):
        """This function will send the next question to the user until it reaches the end of the iteration."""
        # The CallbackData will store the score in namespace "rate" after the separator ":".
        score = self.callback.data.split(":")
        # Get the score.
        if "rate" in score and isinstance(score, list) and len(score) > 1:
            score = score[1]
            self.scores.append(score)
        else:
            score = ""
        await self.callback.answer(text=score)
        try:
            if not score:
                await self.callback.message.answer(text=messages.TYPE_TEACHER_NAME)
            else:
                question = next(self.questions)
                await self.callback.message.answer(text=question, reply_markup=self.inline_rate_keyboard)
        except StopIteration as e:
            self.reset_generator()
            # Insert scores into DB.
            app.sql.update_teachers_in_db(self.name_id, self.scores)
            await self.callback.message.answer("Done")
            from Help import Help
            await Help(bot=self.bot, dp=self.dp, callback=self.callback).answer()
        except FileNotFoundError as e:
            await self.callback.message.answer("Internal error, no available questions")
            from Help import Help
            await Help(bot=self.bot, dp=self.dp, callback=self.callback).answer()


    def __register(self):
        self.dp.register_callback_query_handler(
            self.rate_teacher_callback_handler,
            self.cb_score_filter.filter(),
            state=BotStates.rate
        )
        self.dp.register_message_handler(
            self.teacher_name_callback_handler,
            state=BotStates.rate
        )