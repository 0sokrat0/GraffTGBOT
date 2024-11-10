import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram_dialog import StartMode, DialogManager
from aiogram.types import Message
import aiohttp
from core.states.StartSG import StartSG
from core.config_data.config import Config, Server
from core.config_data.config import load_config
from core.states.ContactSG import ContactSG

from aiogram import Bot, Dispatcher
from aiogram.enums import ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, Message
from aiogram_dialog import Dialog, DialogManager, setup_dialogs, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Next
from aiogram_dialog.widgets.text import Const


start_router = Router()
logger = logging.getLogger(__name__)

config = load_config()


async def get_user(tg_id: int):
    get_user_url = f"{config.server.url}/users/{tg_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(get_user_url) as response:
            if response.status == 200:
                logger.info("Пользователь найден в базе данных.")
                return await response.json()  # Пользователь найден, возвращаем его данные
            elif response.status == 404:
                logger.info("Пользователь не найден, требуется регистрация.")
                return None  # Пользователь не найден
            else:
                logger.error(f"Ошибка при запросе пользователя: {response.status}")
                return f"Error: {response.status}"  # Ошибка при выполнении запроса


async def get_or_create_user(tg_id: int, username: str, phone: str):
    user = await get_user(tg_id)
    if user is not None:
        return user  # Пользователь уже существует

    create_user_url = f"{config.server.url}/users"
    user_data = {"tgID": tg_id, "username": username, "phone": phone}

    async with aiohttp.ClientSession() as session:
        async with session.post(create_user_url, json=user_data) as create_response:
            if create_response.status == 201:
                # Если успешное создание, просто возвращаем подтверждение
                return "User created successfully"
            elif create_response.status == 409:
                return "User already exists"
            else:
                return f"Failed to create user: {create_response.status}"


            
@start_router.message(CommandStart())
async def cmd_start(msg: Message, dialog_manager: DialogManager):
    tg_id = msg.from_user.id
    user = await get_user(tg_id)

    if user is None:
        logger.info(f"Запуск диалога для запроса контакта для пользователя с tg_id={tg_id}")
        await dialog_manager.start(ContactSG.start, mode=StartMode.RESET_STACK)
    else:
        logger.info(f"Пользователь с tg_id={tg_id} уже зарегистрирован.")
        await dialog_manager.start(StartSG.start, mode=StartMode.RESET_STACK)


async def get_contact(msg: Message, _, dialog_manager: DialogManager):
    await msg.bot.delete_message(msg.chat.id, dialog_manager.dialog_data["message_id"])
    await dialog_manager.done()
    print(msg.contact.phone_number)
    phone = msg.contact.phone_number
    tg_id = msg.from_user.id
    username = msg.from_user.username or "Anonymous"
    result = await get_or_create_user(tg_id, username, phone)
    await dialog_manager.start(StartSG.start, mode=StartMode.RESET_STACK)
     


async def send_contact(cq: CallbackQuery, _, dialog_manager: DialogManager):
    markup = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text="📲 Поделиться контактом", request_contact=True)
    ]], resize_keyboard=True)
    message = await cq.message.answer("Нажмите на кнопку ниже 👇", reply_markup=markup)
    dialog_manager.dialog_data["message_id"] = message.message_id