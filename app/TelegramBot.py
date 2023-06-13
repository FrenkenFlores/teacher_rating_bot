import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, Update
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData
import messages
from BotStates import BotStates
from Start import Start
from BotMiddleware import BotMiddleware
import sql

class TelegramBot:
    def __init__(self, token):
        # Set logging format.
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        # Create Bot instance, Bot class inherits from BaseBot class that accepts in the __init__() magic method the
        # Telegram token. The token will be stored in Contextvar "BotDifferentToken". It will be used when a request
        # will be sent to https://api.telegram.org/bot<token>/METHOD_NAME with the aiohttp module. In general,
        # Bot is the main interface to interact with Telegram API. Bot current instance can be retrieved from anyway
        # with Bot.get_current() method, metadata can be retrieved using Bot.get_me() method.
        self.bot = Bot(token=token)
        # Set a memory storage that will be used by FSM.
        self.storage = MemoryStorage()
        # OptimizedDispatcher is a customized class that inherits from Dispatcher class, the main difference is that
        # the current one tracks events when the bot gets added to a group or supergroup and save the event results in
        # its instance properties. That way we can track the groups where our bot was added, what permissions it has,
        # and is it available at the moment. Dispatcher is needed to monitor the events and updates that occur
        # and control how the bot function.
        self.dp = Dispatcher(
            bot=self.bot,
            storage=self.storage,
        )
        self.__register()

    async def __start_handler(self, message: Message, state: FSMContext):
        # await state.set_state(BotStates.start)
        await message.answer(
            text=messages.START_MSG,
            parse_mode="HTML",
            reply_markup=Start(bot=self.bot, dp=self.dp).keyboard
        )


    def __register(self):
        self.dp.middleware.setup(BotMiddleware())
        self.dp.register_message_handler(
            callback=self.__start_handler,
            commands=["start"],
        )

    async def __on_bot_startup(self, dp: Dispatcher):
        """This function will be passed to executor.start_pooling() method, it will be executed once the bot starts, it can
        be used to initialize the bot. Also, Aiogram uses Asyncio, the start_pooling() method calls asyncio.get_event_loop()
        then loop.create_task() and after that loop.run_forever(); so, we can add our own async tasks in this function if
        we want them to run asynchronously using asyncio.create_task(some_loop_fun())."""
        meta = await self.bot.get_me()
        logging.debug(meta)
        logging.info(f"Started bot with id={meta['id']}, first_name={meta['first_name']}, username={meta['username']}")

    def run(self):
        # Start the bot. If skip_updates will be set to True, the bot will skip the requests that were sent
        # while the bot was offline.
        executor.start_polling(
            dispatcher=self.dp,
            skip_updates=True,
            on_startup=self.__on_bot_startup,
            on_shutdown=sql.close_db
        )
