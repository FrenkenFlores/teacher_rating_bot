import typing
from aiohttp.helpers import sentinel
import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from credentials import TOKEN
import messages
import interface
import logging
import asyncio
import json
import copy
import pprint
import time
from aiogram.types import BotCommandScope, BotCommandScopeAllGroupChats
from OptimizedDispatcher import OptimizedDispatcher


# Create Bot instance, Bot class inherits from BaseBot class that accepts in the __init__() magic method the
# Telegram token. The token will be stored in Contextvar "BotDifferentToken". It will be used when a request will be
# sent to https://api.telegram.org/bot<token>/METHOD_NAME with the aiohttp module. In general, Bot is the main interface
# to interact with Telegram API. Bot current instance can be retrieved from anyway with Bot.get_current() method,
# metadata can be retrieved using Bot.get_me() method.
bot = Bot(token=TOKEN)
# OptimizedDispatcher is a customized class that inherits from Dispatcher class, the main difference is that the current
# one tracks events when the bot gets added to a group or supergroup and save the event results in its instance
# properties. That way we can track the groups where our bot was added, what permissions it has, and is it available at
# the moment. Dispatcher is needed to monitor the events and updates that occur and control how the bot function.
odp = OptimizedDispatcher(bot=bot)


async def on_bot_startup(_):
    """This function will be passed to executor.start_pooling() method, it will be executed once the bot starts, it can
    be used to initialize the bot. Also, Aiogram uses Asyncio, the start_pooling() method calls asyncio.get_event_loop()
    then loop.create_task() and after that loop.run_forever(); so, we can add our own async tasks in this function if
    we want them to run asynchronously using asyncio.create_task(some_loop_fun())."""
    meta = await bot.get_me()
    logging.debug(meta)
    logging.info(f"Started bot with id={meta['id']}, first_name={meta['first_name']}, username={meta['username']}")


@odp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    odp = Dispatcher.get_current()
    kb = interface.StartKeyboard(odp).keyboard
    await message.answer(
        text=messages.START_MSG,
        parse_mode="HTML",
        reply_markup=kb
    )
    await message.delete()


@odp.message_handler(Text(equals=messages.HANDLER_ADD_TEACHER))
async def start_handler(message: types.Message):
    await message.delete()


def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    executor.start_polling(
        dispatcher=odp,
        skip_updates=True,
        on_startup=on_bot_startup
    )


# When the current file gets passed to the interpreter, the __name__ global variable will be set to "__main__". That
# means that the main function will only run, when the current file will be executed.
if __name__ == "__main__":
    main()

