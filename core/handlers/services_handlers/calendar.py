import logging
from datetime import datetime, date

from aiogram.client.session import aiohttp
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode

from core.config_data.config import load_config
from core.states.ServicesSG import ServicesSG

config = load_config()
logger = logging.getLogger(__name__)


async def fetch_work_schedule(specialist_id: int):
    url = f"{config.server.url}/work_schedules/specialist/{specialist_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 404:
                return []  # Если расписание отсутствует
            else:
                response_text = await response.text()
                raise Exception(f"Ошибка при запросе расписания: {response.status} {response_text}")


async def base_data_getter(dialog_manager: DialogManager, **kwargs):
    """
    Получить данные для отображения в календаре.
    """
    # Получаем ID специалиста из состояния FSM
    fsm_data = await dialog_manager.middleware_data["state"].get_data()
    specialist_id = fsm_data.get("selected_specialist_id")

    # Запрашиваем расписание специалиста
    try:
        work_schedule = await fetch_work_schedule(specialist_id)
    except Exception as e:
        # Логируем ошибки, если что-то пошло не так
        print(f"Ошибка при получении расписания: {e}")
        return {"work_days": set()}

    # Формируем список рабочих дней
    work_days = set(schedule["day_of_week"] for schedule in work_schedule)

    return {"work_days": work_days}


async def on_date_selected(event, widget, manager: DialogManager, selected_date: date):
    """
    Обработчик выбора даты.
    """
    # Проверяем, является ли выбранная дата рабочей
    work_days = manager.dialog_data.get("work_days", set())
    if selected_date.isoformat() not in work_days:
        await event.answer("Записи закрыты")
        return  # Не переходим к следующему шагу

    # Сохраняем выбранную дату
    await manager.middleware_data["state"].update_data(selected_date=selected_date)
    logger.info(f"Выбранная дата: {selected_date}")

    # Переход к следующему состоянию
    await manager.next()
    await event.answer("Дата успешно выбрана.")



async def handle_registration(callback: CallbackQuery, button, dialog_manager: DialogManager):
    """
    Обработчик начала диалога с выбором специалиста.
    """
    await dialog_manager.start(ServicesSG.set_specialist, mode=StartMode.NORMAL)

async def base_data_getter(dialog_manager: DialogManager, **kwargs):
    fsm_data = await dialog_manager.middleware_data["state"].get_data()
    specialist_id = fsm_data.get("selected_specialist_id")

    try:
        work_schedule = await fetch_work_schedule(specialist_id)
    except Exception as e:
        print(f"Ошибка при получении расписания: {e}")
        return {"work_days": set()}

    work_days = {
        schedule["date"] for schedule in work_schedule
        if datetime.strptime(schedule["date"], "%Y-%m-%d").date() >= datetime.now().date()
    }

    print(f"Рабочие дни специалиста: {work_days}")
    dialog_manager.dialog_data["work_days"] = work_days  # Передача рабочих дней в dialog_data
    return {"work_days": work_days}
