import logging
from datetime import datetime

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode

from core.config_data.config import load_config
from core.states.ServicesSG import ServicesSG

config = load_config()
logger = logging.getLogger(__name__)



async def on_date_selected(event, widget, manager: DialogManager, selected_date: datetime.date):
    """
    Обработчик выбора даты.
    """
    logger.info(f"Дата выбрана: {selected_date}")

    # Сохранение выбранной даты в FSM
    await manager.middleware_data["state"].update_data(selected_date=selected_date)

    await manager.next()
    await event.answer()


async def handle_registration(callback: CallbackQuery, button, dialog_manager: DialogManager):
    """
    Обработчик начала диалога с выбором специалиста.
    """
    await dialog_manager.start(ServicesSG.set_specialist, mode=StartMode.NORMAL)


async def base_data_getter(dialog_manager: DialogManager, **kwargs):
    """
    Пустой геттер данных.
    """
    return {}
