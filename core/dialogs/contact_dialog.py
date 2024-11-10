from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from core.handlers.start import get_contact, send_contact
from core.states.ContactSG import ContactSG
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Next

from aiogram.enums import ContentType

contact_dialog = Dialog(
        Window(
        Const("Привет!"),
        Next(Const("Дальше"), on_click=send_contact),
        state=ContactSG.start
    ),
    Window(
        Const("Чтобы продолжить пользоваться ботом, вам нужно подтвердить свой номер."),
        MessageInput(get_contact, ContentType.CONTACT),
        state=ContactSG.contact
    )
)
