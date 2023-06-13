from credentials import TOKEN
from TelegramBot import TelegramBot
if __name__ == "__main__":
    bot = TelegramBot(token=TOKEN)
    bot.run()
