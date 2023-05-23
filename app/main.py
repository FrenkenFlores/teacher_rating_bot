from aiogram import Bot, Dispatcher, executor, types
from credentials import TOKEN
import messages
import interface
import logging


bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)


async def on_bot_startup(_):
    meta = await bot.get_me()
    logging.debug(meta)
    logging.info(f"Started bot with id={meta['id']}, first_name={meta['first_name']}, username={meta['username']}")

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    kb = interface.StartKeyboard(dp).keyboard
    await message.answer(
        text=messages.START_MSG,
        reply_markup=kb
    )



def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    executor.start_polling(
        dispatcher=dp,
        skip_updates=True,
        on_startup=on_bot_startup
    )


if __name__ == "__main__":
    main()
