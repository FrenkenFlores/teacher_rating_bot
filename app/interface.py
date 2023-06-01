import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import Dispatcher, Bot
from OptimizedDispatcher import OptimizedDispatcher
import messages

class StartKeyboard:
    BUTTON_1 = "add_teacher"
    BUTTON_2 = "rate_teacher"

    def __init__(self, odp: Dispatcher):
        self.keyboard = InlineKeyboardMarkup()
        self.button_rate_teacher = InlineKeyboardButton(text=messages.BUTTON_ADD_TEACHER, callback_data="add_teacher")
        self.button_add_teacher = InlineKeyboardButton(text=messages.BUTTON_RATE_TEACHER, callback_data="rate_teacher")
        self.keyboard.add(self.button_add_teacher)
        self.keyboard.add(self.button_rate_teacher)
        self.odp = odp

        @self.odp.callback_query_handler(text="rate_teacher")
        async def rate_teacher(callback: CallbackQuery):
            bot_id = callback.message["from"]["id"]
            group_id = callback.message["chat"]["id"]
            valid, msg = await self.check_groups(self, bot_id, group_id)
            if valid:
                await callback.answer(text="оценть")
                await callback.message.answer(msg)
            else:
                await callback.answer(text="Ошибка")
                await callback.message.answer(msg)

        @self.odp.callback_query_handler(text="add_teacher")
        async def add_teacher(callback: CallbackQuery):
            bot_id = callback.message["from"]["id"]
            user_id = callback.message["chat"]["id"]
            valid, msg = await self.check_groups(self, bot_id, user_id, check_admin=True)
            if valid:
                await callback.answer(text="добавить")
                await callback.message.answer(msg)
            else:
                await callback.answer(text="Ошибка")
                await callback.message.answer(msg)
    @staticmethod
    async def check_groups(instance, bot_id: str, user_id: str, check_admin=False):
        """Check that the bot and user belong to the same group.
        This funtcion returns a tuple that holds boolean indicator and string message."""
        groups: dict = instance.odp.get_groups()
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
