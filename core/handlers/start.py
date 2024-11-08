import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram_dialog import StartMode, DialogManager
from aiogram.types import Message

from core.states.StartSG import StartSG

start_router = Router()
logger = logging.getLogger(__name__)



@start_router.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):

    await dialog_manager.start(state = StartSG.start, mode = StartMode.RESET_STACK)
