from aiogram.dispatcher.filters.state import StatesGroup, State

class BotStates(StatesGroup):
    start = State()
    help = State()
    add = State()
    remove = State()
    rate = State()
    get = State()
