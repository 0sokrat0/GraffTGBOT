from aiogram.fsm.state import StatesGroup, State

class ServicesSG(StatesGroup):
    set_specialist = State()
    set_services = State()
    set_date = State()

