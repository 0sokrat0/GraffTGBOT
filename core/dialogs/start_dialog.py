from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from core.handlers import handle_contact, handle_profile, handle_services, handle_registration
from core.states.StartSG import StartSG

# Диалоговое окно панели администратора
start_dialog = Dialog(
    Window(
        Const('👋 Добро пожаловать в барбершоп <b>"Graff"</b>!\n\n'
              'Здесь вы можете:\n'
              '- 📅 <b>Записаться</b> на стрижку или бритье.\n'
              '- 💈 Узнать о <b>услугах</b> и ценах.\n'
              '- 👤 Проверить свой <b>профиль</b> и записи.\n'
              '- ☎️ Связаться с нами через <b>звонок</b>.\n\n'
              'Для помощи нажмите ℹ️ <b>Помощь</b>.\n\n'
              'Спасибо, что выбрали нас! 🎩'),
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
        state=StartSG.start,
    ),
)
