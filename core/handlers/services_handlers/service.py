import json
import logging
import operator
from typing import Optional, List, Dict, Any

import aiohttp
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select, Radio
from aiogram_dialog.widgets.text import Format

from core.config_data.config import load_config

config = load_config()
logger = logging.getLogger(__name__)


async def get_services() -> Optional[List[Dict[str, Any]]]:
    """
    Получение списка услуг с API.
    """
    get_services_url = f"{config.server.url}/services"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(get_services_url) as response:
                content_type = response.headers.get('Content-Type', '')
                logger.info(f"Content-Type: {content_type}")
                if response.status == 200:
                    if 'application/json' in content_type:
                        services = await response.json()
                        logger.info(f"Получено услуг: {services}")
                        return services
                    else:
                        text = await response.text()
                        try:
                            services = json.loads(text)
                            logger.info(f"Получено услуг (ручная декодировка): {services}")
                            return services
                        except json.JSONDecodeError:
                            logger.error("Не удалось декодировать ответ как JSON.")
                            return None
                elif response.status == 404:
                    logger.info("Услуги не найдены.")
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка при запросе услуг: {response.status}, {error_text}")
                    return None
    except aiohttp.ClientError as e:
        logger.exception(f"Сетевая ошибка при запросе услуг: {e}")
        return None


async def get_service_data(dialog_manager: DialogManager, state: FSMContext, **kwargs) -> Dict[str, Any]:
    """
    Геттер данных услуг для отображения в диалоге.
    """
    services = await get_services()
    if services:
        services_list = [{'name': service['name'], 'id': int(service['id'])} for service in services]
    else:
        services_list = []

    # Сохраняем услуги в FSM
    await state.update_data(services=services_list)
    logger.debug(f"Сохранено в FSM: {services_list}")
    return {'services': services_list}


async def handle_service_selected(
    callback: CallbackQuery,
    widget: Radio,
    manager: DialogManager,
    item_id: str
):
    """
    Обработчик выбора услуги.
    """
    logger.info(f"[SERVICE SELECTED] Выбрана услуга с ID: {item_id}")

    # Сохраняем выбранную услугу в FSM
    await manager.middleware_data["state"].update_data(selected_service_id=int(item_id))

    # Логируем текущее состояние FSM
    current_state_data = await manager.middleware_data["state"].get_data()
    logger.debug(f"[FSM DATA AFTER SERVICE SELECTED] {current_state_data}")

    # Подтверждение выбора
    await callback.message.edit_text(f"Вы выбрали услугу: <b>{item_id}</b>.", parse_mode="HTML")
    await manager.next()


async def service_data_getter(dialog_manager: DialogManager, **kwargs):
    return await get_service_data(dialog_manager, dialog_manager.middleware_data["state"])



services_kbd = Radio(
    checked_text=Format("🔘 {item[name]}"),
    unchecked_text=Format("⚪ {item[name]}"),
    id="services_radio",
    item_id_getter=operator.itemgetter("id"),
    items="services",
    on_click=handle_service_selected,
)

