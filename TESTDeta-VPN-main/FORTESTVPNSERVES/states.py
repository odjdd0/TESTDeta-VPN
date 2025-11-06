from aiogram.dispatcher.filters.state import State, StatesGroup

class UserState(StatesGroup):
    AwaitingAgreement = State()
    MainMenu = State()
    AwaitingNewConfig = State()
    AwaitingBroadcastText = State()
    AwaitingBroadcastPhoto = State()
    AwaitingBroadcastUrl = State()