# core/states/ContactSG.py
from aiogram.fsm.state import State, StatesGroup

class ContactSG(StatesGroup):
    start = State()      # Начальное состояние
    contact = State()    #