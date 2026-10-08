from aiogram.fsm.state import State, StatesGroup

class Reg(StatesGroup):
    name = State()
    age = State()
    gender = State()
    looking = State()
    city = State()
    bio = State()
    photo = State()

class Report(StatesGroup):
    reason = State()