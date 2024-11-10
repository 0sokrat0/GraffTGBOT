from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format
from aiogram.types import Message

from core.handlers import handle_profile, handle_registration, handle_services, handle_contact
from core.states.StartSG import StartSG


async def get_username_data(dialog_manager: DialogManager, **kwargs):
    # Access the username from the dialog_manager event context
    username = dialog_manager.event.from_user.username if dialog_manager.event and dialog_manager.event.from_user else "User"
    return {
        "username": username
    }

# Диалоговое окно с приветственным сообщением
start_dialog = Dialog(
    Window(
        Format(
            '👋 Добро пожаловать в барбершоп <b>"Graff"</b>, <b>{username}</b>!\n\n'
            'Здесь вы можете:\n'
            '- 📅 <b>Записаться</b> на стрижку или бритье.\n'
            '- 💈 Узнать о <b>услугах</b> и ценах.\n'
            '- 👤 Проверить свой <b>профиль</b> и записи.\n'
            '- ☎️ Связаться с нами через <b>звонок</b>.\n\n'
            'Спасибо, что выбрали нас! 🎩'
        ),
        Button(
            text=Const('📅 Запись'),
            id='register_button',
            on_click=handle_registration),
        Button(
            text=Const('💈 Услуги'),
            id='services_button',
            on_click=handle_services),
        Button(
            text=Const('👤 Профиль'),
            id='profile_button',
            on_click=handle_profile),
        Button(
            text=Const('☎️ Звонок'),
            id='contact_button',
            on_click=handle_contact),
        getter=get_username_data,  # Привязка функции для передачи данных о пользователе
        state=StartSG.start,
    ),
)
