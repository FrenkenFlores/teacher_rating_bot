import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import Dispatcher, Bot
from OptimizedDispatcher import OptimizedDispatcher
import messages
import json
from aiogram.utils.callback_data import CallbackData
from BotStates import BotStates
import sql
QUESTIONS_PATH = "questions.json"



class AddTeacher:
    """This class will represent the teacher addition process."""
    def __init__(self, odp: Dispatcher, callback: CallbackQuery):
        self.odp = odp
        self.callback = callback

    async def answer(self):
        await self.callback.answer()
        await self.callback.message.answer(messages.TYPE_TEACHER_NAME)


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







class Start:
    """This is the class that represents the starting window."""
    # The
    ADD_TEACHER_CB_DATA = "add_teacher"
    RATE_TEACHER_CB_DATA = "rate_teacher"
    GET_RATE_CB_DATA = "get_rate"

    def __init__(self, bot: Bot, dp: Dispatcher):
        self.callback_filter = CallbackData("state", "start")
        self.keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=messages.BUTTON_ADD_TEACHER, callback_data=self.callback_filter.new(self.ADD_TEACHER_CB_DATA))],
            [InlineKeyboardButton(text=messages.BUTTON_RATE_TEACHER, callback_data=self.callback_filter.new(self.RATE_TEACHER_CB_DATA))],
            [InlineKeyboardButton(text=messages.BUTTON_LIST_TEACHER, callback_data=self.callback_filter.new(self.GET_RATE_CB_DATA))]
        ])
        self.bot = bot
        self.dp = dp
        self.__register()

    async def get_list(self, callback: CallbackQuery):
        bot_id = callback.message["from"]["id"]
        group_id = callback.message["chat"]["id"]
        valid, msg = await self.check_groups(bot_id, group_id)
        if valid:
            await RateTeacherQuestion(odp=self.dp, callback=callback).answer()
        else:
            await callback.answer(text="Ошибка")
            await callback.message.answer(msg)

    async def add_teacher(self, callback: CallbackQuery):
        bot_id = callback.message["from"]["id"]
        user_id = callback.message["chat"]["id"]
        valid, msg = await self.check_groups(bot_id, user_id, check_admin=True)
        if valid:
            await AddTeacher(odp=self.dp, callback=callback).answer()
        else:
            await callback.answer(text="Ошибка")
            await callback.message.answer(msg)

    async def rate_teacher(self, callback: CallbackQuery):
        bot_id = callback.message["from"]["id"]
        group_id = callback.message["chat"]["id"]
        valid, msg = await self.check_groups(bot_id, group_id)
        if valid:
            await RateTeacherQuestion(odp=self.dp, callback=callback).answer()
        else:
            await callback.answer(text="Ошибка")
            await callback.message.answer(msg)

    @staticmethod
    async def check_groups(bot_id: str, user_id: str, check_admin=False):
        """Check that the bot and user belong to the same group.
        This function returns a tuple that holds boolean indicator and string message."""
        groups: dict = sql.get_chats_dict_from_db()
        # Check if the bot is added to any group.
        if not groups:
            return False, messages.TYPE_TEACHER_NAME_ERROR_NO_GROUP
        # If there is groups.
        else:
            bot = Bot.get_current()
            # Iterate over the ID of the group.
            for group in groups.keys():
                # Check if the user and group belong to the current group.
                try:
                    bot_member = await bot.get_chat_member(int(group), int(bot_id))
                    user_member = await bot.get_chat_member(int(group), int(user_id))
                except Exception as e:
                    logging.error(e)
                    return False, messages.TYPE_TEACHER_NAME_ERROR_BOT_KICKED
                if not bot_member.is_chat_member():
                    continue
                if not user_member.is_chat_member():
                    continue
                elif user_member.is_chat_member():
                    if check_admin and not user_member.is_chat_admin():
                        return False, messages.TYPE_TEACHER_NAME_ERROR_NO_ADMIN
                return True, (messages.HANDLER_ADD_TEACHER if check_admin else messages.HANDLER_RATE_TEACHER)
        return False, messages.TYPE_TEACHER_NAME_ERROR_NO_USER

    def __register(self):
        self.dp.register_callback_query_handler(self.add_teacher, self.callback_filter.filter(start=self.ADD_TEACHER_CB_DATA))
        self.dp.register_callback_query_handler(self.rate_teacher, self.callback_filter.filter(start=self.RATE_TEACHER_CB_DATA))
        self.dp.register_callback_query_handler(self.get_list, self.callback_filter.filter(start=self.GET_RATE_CB_DATA))

