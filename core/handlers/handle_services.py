# core/handlers/handle_services.py
import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from datetime import datetime

from core.states.CalendarSG import CalendarEventStates


logger = logging.getLogger(__name__)

async def handle_registration(callback: CallbackQuery, button, dialog_manager: DialogManager):
    """
    Обработчик нажатия на кнопку "Запись".
    """
    await dialog_manager.start(CalendarEventStates.set_date, mode=StartMode.RESET_STACK)



async def on_date_selected(event, source, manager: DialogManager, selected_date: datetime.date):
    """
    Обработчик выбранной даты из календаря.
    """
    logger.info(f"Дата выбрана: {selected_date}")

    # Сохранение выбранной даты в диалоговом контексте
    context = manager.current_context()
    context.dialog_data["selected_date"] = selected_date

    # Завершение диалога и передача результата
    await manager.done(result=selected_date)

    # (Опционально) Отправка сообщения пользователю
    await manager.event.bot.send_message(
        chat_id=event.from_user.id,
        text=f"Вы выбрали дату: {selected_date.strftime('%d.%m.%Y')}"
    )
async def base_data_getter(dialog_manager: DialogManager, **kwargs):
    """
    Getter для предоставления данных в диалог.
    """
    return {}
