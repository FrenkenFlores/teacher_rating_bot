from aiogram import Dispatcher
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
import json
import messages


QUESTIONS_PATH = "questions.json"


class RateTeacherQuestion:
    """This class will represent the rating process."""
    def __init__(self, odp: Dispatcher, callback: CallbackQuery):
        """__init__ will take two arguments, the current Dispatcher and the first callback that was
        received from the caller function. __init__ will initialize the score keyboard and the
        generator of the questions."""
        self.cb_score_filter = CallbackData("rate", "score")
        # Add inline keyboard with the buttons that represent the score.
        self.inline_rate_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="1️⃣", callback_data=self.cb_score_filter.new("1")),
                InlineKeyboardButton(text="2️⃣", callback_data=self.cb_score_filter.new("2")),
                InlineKeyboardButton(text="3️⃣", callback_data=self.cb_score_filter.new("3")),
                InlineKeyboardButton(text="4️⃣", callback_data=self.cb_score_filter.new("4")),
                InlineKeyboardButton(text="5️⃣", callback_data=self.cb_score_filter.new("5"))],
                [InlineKeyboardButton(text="6️⃣", callback_data=self.cb_score_filter.new("6")),
                InlineKeyboardButton(text="7️⃣", callback_data=self.cb_score_filter.new("7")),
                InlineKeyboardButton(text="8️⃣", callback_data=self.cb_score_filter.new("8")),
                InlineKeyboardButton(text="9️⃣", callback_data=self.cb_score_filter.new("9")),
                InlineKeyboardButton(text="🔟", callback_data=self.cb_score_filter.new("10"))]
            ]
        )
        # Set the current Dispatcher.
        self.odp = odp
        # Set the first callback.
        self.callback = callback
        # Init the generator of the questions.
        self.questions = self.get_question()
        @self.odp.callback_query_handler(self.cb_score_filter.filter())
        async def add_teacher_callback_handler(callback: CallbackQuery):
            self.callback = callback
            await self.answer()

    def get_question(self):
        """This is a generator function, it will return the next question after receiving callback query from
        the rating inline keyboard."""
        with open(QUESTIONS_PATH, "r") as json_questions:
            questions = json.load(json_questions)
        if not questions:
            raise FileNotFoundError
        for q in questions:
            yield q

    async def answer(self):
        """This function will send the next question to the user until it reaches the end of the iteration."""
        # The CallbackData will store the score in namespace "rate" after the separator ":".
        score = self.callback.data.split(":")
        if isinstance(score, list) and len(score) > 1:
            score = score[1]
        else:
            score = ""
        await self.callback.answer(text=score)
        try:
            question = next(self.questions)
            await self.callback.message.answer(question, reply_markup=self.inline_rate_keyboard)
        except StopIteration as e:
            await self.callback.message.answer("Done")
        except FileNotFoundError as e:
            await self.callback.message.answer("Internal error, no available questions")

