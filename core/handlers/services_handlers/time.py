import datetime
import json

import aiohttp
import logging
from operator import itemgetter
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Radio
from aiogram_dialog.widgets.text import Format, Const
from aiogram.types import CallbackQuery

from core.config_data.config import load_config

logger = logging.getLogger(__name__)
config = load_config()


async def get_fsm_data(dialog_manager: DialogManager, keys: list[str]):
    """
    Извлекает данные из FSM по указанным ключам.

    :param dialog_manager: Объект DialogManager.
    :param keys: Список ключей, которые нужно получить из FSM.
    :return: Словарь с данными по ключам.
    """
    try:
        state_data = await dialog_manager.middleware_data["state"].get_data()
        extracted_data = {key: state_data.get(key) for key in keys}

        # Логирование данных
        logger.debug(f"[FSM DATA] Извлеченные данные: {extracted_data}")

        # Проверка на наличие недостающих данных
        missing_keys = [key for key, value in extracted_data.items() if value is None]
        if missing_keys:
            logger.warning(f"[FSM DATA] Недостающие ключи: {missing_keys}")

        return extracted_data
    except Exception as e:
        logger.exception(f"[FSM DATA] Ошибка при извлечении данных: {e}")
        return {}


async def fetch_available_times(service_id: int, specialist_id: int, booking_date: str):
    """
    Запрос к API для получения доступного времени.
    """
    url = f"{config.server.url}/available_times"

    # Проверяем, что все параметры заданы
    if not service_id or not specialist_id or not booking_date:
        logger.error("Некорректные параметры для запроса доступного времени")
        return []

    # Если booking_date - объект datetime.date, преобразуем его в строку
    if isinstance(booking_date, (datetime.date, datetime)):
        booking_date = booking_date.strftime("%Y-%m-%d")

    params = {
        "service_id": service_id,
        "specialist_id": specialist_id,
        "booking_date": booking_date,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                # Обработка JSON-ответа
                if response.headers.get("Content-Type", "").startswith("application/json"):
                    return await response.json()  # Список доступных временных интервалов
                else:
                    # Если не JSON, попробуем обработать как текст
                    text = await response.text()
                    logger.warning(f"[FETCH AVAILABLE TIMES] Non-JSON response: {text}")
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        logger.error("Ответ API не соответствует формату JSON.")
                        return []
    except Exception as e:
        logger.exception(f"Ошибка при запросе доступного времени: {e}")
        return []


# Widget Radio для отображения времени
async def available_times_getter(dialog_manager: DialogManager, **kwargs):
    """
    Геттер для получения доступного времени и передачи его в Radio-кнопки.
    """
    fsm_data = await get_fsm_data(dialog_manager, ["selected_service_id", "selected_specialist_id", "selected_date"])
    service_id = fsm_data.get("selected_service_id")
    specialist_id = fsm_data.get("selected_specialist_id")
    booking_date = fsm_data.get("selected_date")

    if not service_id or not specialist_id or not booking_date:
        logger.error(f"[AVAILABLE TIMES] Недостаточно данных для запроса времени: {fsm_data}")
        return {"available_times": []}

    # Логируем параметры перед запросом
    logger.debug(f"[AVAILABLE TIMES] Запрашиваем доступное время для service_id={service_id}, specialist_id={specialist_id}, booking_date={booking_date}")

    available_times = await fetch_available_times(service_id, specialist_id, booking_date)

    if not available_times:
        logger.warning(f"[AVAILABLE TIMES] Нет доступных временных интервалов для service_id={service_id}, specialist_id={specialist_id}, booking_date={booking_date}")
        return {"available_times": []}

    times = [(time, time) for time in available_times]
    logger.debug(f"[AVAILABLE TIMES] Доступные временные интервалы: {times}")
    return {"available_times": times}


# Radio Widget
times_kbd = Radio(
    checked_text = Format("🔘 {item[0]}"),
    unchecked_text = Format("⚪ {item[0]}"),
    id = "r_times",
    item_id_getter = itemgetter(1),  # Берем ID элемента
    items = "available_times",  # Данные из геттера
)


# Обработчик выбора времени
async def on_time_selected(callback: CallbackQuery, widget: Radio, manager: DialogManager, item_id: str):
    """
    Обработчик выбора времени.
    """
    logger.info(f"[TIME SELECTED] Пользователь выбрал время: {item_id}")

    # Сохраняем время в FSM
    await manager.middleware_data["state"].update_data(selected_time=item_id)

    # Логируем текущее состояние FSM
    current_state_data = await manager.middleware_data["state"].get_data()
    logger.debug(f"[FSM DATA AFTER TIME SELECTED] Текущее состояние FSM: {current_state_data}")

    # Подтверждаем выбор
    await callback.message.edit_text(f"Вы выбрали время: <b>{item_id}</b>.", parse_mode="HTML")
    await manager.next()
