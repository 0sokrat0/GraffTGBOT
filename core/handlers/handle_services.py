import logging
import json
from typing import Optional, List, Dict, Any
import aiohttp
from datetime import datetime
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Select
from aiogram.fsm.context import FSMContext

from core.config_data.config import load_config
from core.states.ServicesSG import ServicesSG

config = load_config()
logger = logging.getLogger(__name__)


async def get_specialists() -> Optional[List[Dict[str, Any]]]:
    """
    Получение списка специалистов с API.
    """
    get_specialist_url = f"{config.server.url}/specialists"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(get_specialist_url) as response:
                content_type = response.headers.get('Content-Type', '')
                logger.info(f"Content-Type: {content_type}")
                if response.status == 200:
                    if 'application/json' in content_type:
                        specialists = await response.json()
                        logger.info(f"Получено специалистов: {specialists}")
                        return specialists
                    else:
                        text = await response.text()
                        try:
                            specialists = json.loads(text)
                            logger.info(f"Получено специалистов (ручная декодировка): {specialists}")
                            return specialists
                        except json.JSONDecodeError:
                            logger.error("Не удалось декодировать ответ как JSON.")
                            return None
                elif response.status == 404:
                    logger.info("Специалисты не найдены.")
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка при запросе специалистов: {response.status}, {error_text}")
                    return None
    except aiohttp.ClientError as e:
        logger.exception(f"Сетевая ошибка при запросе специалистов: {e}")
        return None


async def get_specialists_data(dialog_manager: DialogManager, state: FSMContext, **kwargs) -> Dict[str, Any]:
    """
    Геттер данных специалистов для отображения в диалоге.
    """
    specialists = await get_specialists()
    if specialists:
        specialists_list = [{'name': spec['name'], 'id': int(spec['id'])} for spec in specialists]
    else:
        specialists_list = []

    # Сохраняем специалистов в FSM
    await state.update_data(specialists=specialists_list)
    logger.debug(f"Сохранено в FSM: {specialists_list}")
    return {'specialists': specialists_list}


async def handle_specialist_selected(
    event: CallbackQuery,
    widget: Select,
    manager: DialogManager,
    item_id: Any
):
    """
    Обработчик выбора специалиста.
    """
    logger.debug("=== Обработчик handle_specialist_selected ===")
    logger.debug(f"Событие: {event}")
    logger.debug(f"Item ID: {item_id} (тип: {type(item_id)})")

    try:
        item_id = int(item_id)
    except ValueError:
        logger.error(f"Неверный формат item_id: {item_id}")
        await event.answer("Произошла ошибка при выборе специалиста.")
        return

    # Получение специалистов из FSM
    fsm_data = await manager.middleware_data["state"].get_data()
    specialists = fsm_data.get('specialists', [])
    logger.debug(f"Специалисты из FSM: {specialists}")

    # Поиск специалиста
    specialist = next((s for s in specialists if s['id'] == item_id), None)
    if not specialist:
        logger.error(f"Специалист с ID {item_id} не найден.")
        await event.answer("Произошла ошибка при выборе специалиста.")
        return

    name = specialist.get('name', 'Неизвестно')
    logger.info(f"Выбран специалист: {name} с ID: {item_id}")

    # Сохранение выбранного специалиста в FSM
    await manager.middleware_data["state"].update_data(selected_specialist_id=item_id)

    # Обновляем сообщение
    await event.message.edit_text(
        f"Вы выбрали специалиста: <b>{name}</b> с ID: <code>{item_id}</code>",
        parse_mode='HTML'
    )

    # Переход к следующему состоянию
    await manager.next()
    await event.answer()


async def on_date_selected(event, widget, manager: DialogManager, selected_date: datetime.date):
    """
    Обработчик выбора даты.
    """
    logger.info(f"Дата выбрана: {selected_date}")

    # Сохранение выбранной даты в FSM
    await manager.middleware_data["state"].update_data(selected_date=selected_date)

    # Завершение диалога и передача результата
    await manager.done(result={"date": selected_date})

    # Отправка сообщения пользователю
    await event.message.answer(f"Вы выбрали дату: {selected_date.strftime('%d.%m.%Y')}")


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
