import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram import Dispatcher, Bot
from aiogram.utils.callback_data import CallbackData
from app.BotStates import BotStates
from app.AddTeacher import AddTeacher
from app.RateTeacherQuestion import RateTeacherQuestion
from app.TeachersList import TeachersList
from app.RemoveTeacher import RemoveTeacher
import sql
import messages
import asyncio

class Help:
    """This is the class that represents the final state."""
    ADD_TEACHER_CB_DATA = "add_teacher"
    REMOVE_TEACHER_CB_DATA = "remove_teacher"
    RATE_TEACHER_CB_DATA = "rate_teacher"
    GET_RATE_CB_DATA = "get_rate"

    def __init__(self, bot: Bot, dp: Dispatcher, callback: CallbackQuery = None, message: Message = None):
        self.callback_filter = CallbackData("state", "help")
        self.keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=messages.BUTTON_ADD_TEACHER, callback_data=self.callback_filter.new(self.ADD_TEACHER_CB_DATA))],
            [InlineKeyboardButton(text=messages.BUTTON_REMOVE_TEACHER, callback_data=self.callback_filter.new(self.REMOVE_TEACHER_CB_DATA))],
            [InlineKeyboardButton(text=messages.BUTTON_RATE_TEACHER, callback_data=self.callback_filter.new(self.RATE_TEACHER_CB_DATA))],
            [InlineKeyboardButton(text=messages.BUTTON_LIST_TEACHER, callback_data=self.callback_filter.new(self.GET_RATE_CB_DATA))]
        ])
        self.bot = bot
        self.dp = dp
        self.callback = callback
        self.message = message
        # Set the Help state.
        asyncio.create_task(BotStates.help.set())
        self.__register()

    async def answer(self):
        if self.callback:
            await self.callback.answer("Help")
            await self.callback.message.answer(text=messages.HELP_MSG, parse_mode="HTML", reply_markup=self.keyboard)
        if self.message:
            await self.message.answer(text=messages.HELP_MSG, parse_mode="HTML", reply_markup=self.keyboard)

    async def add_teacher(self, callback: CallbackQuery):
        self.callback = callback
        # TODO: Check bot id, user id, channel id.
        bot_id = callback.message["from"]["id"]
        user_id = callback.message["chat"]["id"]
        valid, msg = await self.check_groups(bot_id, user_id, check_admin=True)
        if valid:
            await AddTeacher(bot=self.bot, dp=self.dp, callback=callback).answer()
        else:
            await callback.answer(text="Ошибка")
            await callback.message.answer(msg)

    async def remove_teacher(self, callback: CallbackQuery):
        bot_id = callback.message["from"]["id"]
        user_id = callback.message["chat"]["id"]
        valid, msg = await self.check_groups(bot_id, user_id, check_admin=True)
        if valid:
            await RemoveTeacher(bot=self.bot, dp=self.dp, callback=callback).answer()
        else:
            await callback.answer(text="Ошибка")
            await callback.message.answer(msg)

    async def rate_teacher(self, callback: CallbackQuery):
        self.callback = callback
        bot_id = callback.message["from"]["id"]
        group_id = callback.message["chat"]["id"]
        valid, msg = await self.check_groups(bot_id, group_id)
        if valid:
            await RateTeacherQuestion(bot=self.bot, dp=self.dp, callback=callback).answer()
        else:
            await callback.answer(text="Ошибка")
            await callback.message.answer(msg)

    async def get_list(self, callback: CallbackQuery):
        self.callback = callback
        bot_id = callback.message["from"]["id"]
        group_id = callback.message["chat"]["id"]
        valid, msg = await self.check_groups(bot_id, group_id)
        if valid:
            await TeachersList(bot=self.bot, dp=self.dp, callback=callback).answer()
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
        self.dp.register_callback_query_handler(
            self.add_teacher,
            self.callback_filter.filter(help=self.ADD_TEACHER_CB_DATA),
            state=BotStates.help
        )
        self.dp.register_callback_query_handler(
            self.remove_teacher,
            self.callback_filter.filter(help=self.REMOVE_TEACHER_CB_DATA),
            state=BotStates.help
        )
        self.dp.register_callback_query_handler(
            self.rate_teacher,
            self.callback_filter.filter(help=self.RATE_TEACHER_CB_DATA),
            state=BotStates.help
        )
        self.dp.register_callback_query_handler(
            self.get_list,
            self.callback_filter.filter(help=self.GET_RATE_CB_DATA),
            state=BotStates.help
        )

