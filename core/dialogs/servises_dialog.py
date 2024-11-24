# core/dialogs/service_dialog.py

from datetime import date
from typing import Dict

from aiogram.enums import ParseMode
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Calendar,
    CalendarScope,
)
from aiogram_dialog.widgets.kbd import Select, Cancel
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarUserConfig
)
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    DATE_TEXT,
    TODAY_TEXT,
    CalendarDaysView,
    CalendarMonthView,
    CalendarScopeView,
    CalendarYearsView,
)
from aiogram_dialog.widgets.text import Const, Format, Text
from aiogram_dialog.widgets.text import Multi
from babel.dates import get_day_names, get_month_names

SELECTED_DAYS_KEY = "selected_dates"
from core.states.ServicesSG import ServicesSG
from core.handlers.handle_services import (
    on_date_selected,
    get_specialists_data,
    handle_specialist_selected,
    base_data_getter
)

class WeekDay(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        return get_day_names(
            width="short", context="stand-alone", locale=locale,
        )[selected_date.weekday()].title()


class MarkedDay(Text):
    def __init__(self, mark: str, other: Text):
        super().__init__()
        self.mark = mark
        self.other = other

    async def _render_text(self, data, manager: DialogManager) -> str:
        current_date: date = data["date"]
        serial_date = current_date.isoformat()
        selected = manager.dialog_data.get(SELECTED_DAYS_KEY, [])
        if serial_date in selected:
            return self.mark
        return await self.other.render_text(data, manager)


class Month(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        return get_month_names(
            "wide", context="stand-alone", locale=locale,
        )[selected_date.month].title()


class CustomCalendar(Calendar):
    def _init_views(self) -> dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data,
                date_text=MarkedDay("🔴", DATE_TEXT),
                today_text=MarkedDay("⭕", TODAY_TEXT),
                header_text="~~~~~ " + Month() + " ~~~~~",
                weekday_text=WeekDay(),
                next_month_text=Month() + " >>",
                prev_month_text="<< " + Month(),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                month_text=Month(),
                header_text="~~~~~ " + Format("{date:%Y}") + " ~~~~~",
                this_month_text="[" + Month() + "]",
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data,
            ),
        }

    async def _get_user_config(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> CalendarUserConfig:
        return CalendarUserConfig(
            firstweekday=7,
        )


service_dialog = Dialog(
    Window(
        Const(text='<b>Выберите специалиста:</b>'),
        Select(
            Format('{item[name]}'),                   # Отображаемое имя специалиста
            id='spec',
            item_id_getter=lambda item: item['id'],   # Лямбда-функция для получения ID
            items='specialists',                      # Соответствует ключу в геттере
            on_click=handle_specialist_selected
        ),
        state=ServicesSG.set_specialist,
        getter=get_specialists_data,
        parse_mode=ParseMode.HTML
    ),
    Window(
        Multi(
            Const('<b>Выберите день 👇</b>'),
            sep='\n',
        ),
        CustomCalendar(id='calendar', on_click=on_date_selected),
        Cancel(
            text=Const('Отменить'),
        ),
        state=ServicesSG.set_date,
        getter=base_data_getter,
        parse_mode=ParseMode.HTML,
    )
)
