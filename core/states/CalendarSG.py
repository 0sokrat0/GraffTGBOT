from aiogram.fsm.state import StatesGroup, State


class CalendarEventStates(StatesGroup):
    set_date = State()
