from aiogram.fsm.state import State, StatesGroup


class RequestForm(StatesGroup):
    object_type = State()
    repair_type = State()
    area = State()
    location = State()
    budget = State()
    start_date = State()
    name = State()
    phone = State()
    confirmation = State()
