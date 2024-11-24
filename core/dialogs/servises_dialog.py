# core/dialogs/service_dialog.py
from aiogram_dialog.widgets.kbd import Button
from datetime import date, datetime
from typing import Dict

from aiogram.enums import ParseMode
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Calendar,
    CalendarScope, Radio, Column, Row,
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

from core.handlers.services_handlers.time import times_kbd, available_times_getter
from core.handlers.services_handlers.calendar import on_date_selected, base_data_getter
from core.handlers.services_handlers.service import services_kbd, service_data_getter
from core.handlers.services_handlers.specialists import handle_specialist_selected, get_specialists_data

SELECTED_DAYS_KEY = "selected_dates"
from core.states.ServicesSG import ServicesSG


class WeekDay(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        return get_day_names(
            width="short", context="stand-alone", locale=locale,
        )[selected_date.weekday()].title()


class MarkedDay(Text):
    def __init__(self, get_work_days, mark_work: str = "", mark_non_work: str = "⬜️"):
        """
        :param get_work_days: функция или множество рабочих дней.
        :param mark_work: эмодзи для рабочих дней.
        :param mark_non_work: эмодзи для нерабочих дней.
        """
        super().__init__()
        self.get_work_days = get_work_days
        self.mark_work = mark_work
        self.mark_non_work = mark_non_work

    async def _render_text(self, data, manager: DialogManager) -> str:
        current_date: date = data["date"]
        serial_date = current_date.isoformat()  # Преобразуем дату в строку "YYYY-MM-DD"
        work_days = (
            self.get_work_days(manager)
            if callable(self.get_work_days)
            else self.get_work_days
        )

        day = current_date.day  # Получаем только день месяца

        if serial_date in work_days:
            return f"{day}"  # Отображаем только число для рабочего дня
        return self.mark_non_work  # Показываем эмодзи для нерабочего дня


class Month(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        return get_month_names(
            "wide", context="stand-alone", locale=locale,
        )[selected_date.month].title()


class CustomCalendar(Calendar):
    def __init__(self, id: str, on_click, work_days):
        """
        :param id: идентификатор календаря.
        :param on_click: обработчик выбора даты.
        :param work_days: функция или множество рабочих дней.
        """
        self._work_days = work_days
        super().__init__(id=id, on_click=on_click)

    def _get_work_days(self, manager: DialogManager):
        # Получаем рабочие дни из `dialog_data`
        if callable(self._work_days):
            return self._work_days({}, manager)
        return self._work_days

    def _init_views(self) -> dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data,
                date_text=MarkedDay(self._get_work_days),  # Динамическое получение рабочих дней
                today_text=MarkedDay(self._get_work_days, mark_work="⭕", mark_non_work="⬜️"),  # Текущий день
                header_text="~~~~~ " + Month() + " ~~~~~",  # Заголовок с месяцем
                weekday_text=WeekDay(),  # Отображение дней недели
                next_month_text=Month() + " >>",  # Кнопка следующего месяца
                prev_month_text="<< " + Month(),  # Кнопка предыдущего месяца
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                month_text=Month(),
                header_text="~~~~~ " + Format("{date:%Y}") + " ~~~~~",  # Год
                this_month_text="[" + Month() + "]",
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data,
            ),
        }


    async def _get_user_config(
        self, data: Dict, manager: DialogManager
    ) -> CalendarUserConfig:
        """
        Настраиваем пользовательский календарь.
        """
        return CalendarUserConfig(
            firstweekday=7,  # Устанавливаем первый день недели (воскресенье)
            min_date=datetime.now().date(),  # Ограничиваем минимальную дату текущим днем
        )

service_dialog = Dialog(
    Window(
        Const(text='<b>Выберите специалиста:</b>'),
        Column(
            Select(
                Format('💈 {item[name]} 💈'),
                id='spec',
                item_id_getter=lambda item: item['id'],
                items='specialists',
                on_click=handle_specialist_selected
            )
        ),
        Row(
            Cancel(text=Const('📛 Отменить')),
        ),
        state=ServicesSG.set_specialist,
        getter=get_specialists_data,
        parse_mode=ParseMode.HTML
    ),
    Window(
        Const(text='<b>Выберите услугу:</b>'),
        Column(services_kbd),
        Row(
            Button(Const('◀️ Назад'), id='back_to_specialist', on_click=lambda c, b, m: m.back()),
            Cancel(text=Const('📛 Отменить'))
        ),
        state=ServicesSG.set_services,
        getter=service_data_getter,
        parse_mode=ParseMode.HTML
    ),
    Window(
        Multi(
            Const('<b>Выберите день 👇</b>'),
            sep = '\n',
        ),
        CustomCalendar(
            id = "calendar",
            on_click = on_date_selected,
            work_days = lambda data, manager: manager.dialog_data.get("work_days", set()),
        ),
        Row(
            Button(Const('◀️ Назад'), id = 'back_to_services', on_click = lambda c, b, m: m.back()),
            Cancel(text = Const('📛 Отменить'))
        ),
        state = ServicesSG.set_date,
        getter = base_data_getter,
        parse_mode = ParseMode.HTML,
    ),
    Window(
        Const("<b>Выберите время для записи:</b>"),
        Column(times_kbd),
        Row(
            Button(Const('◀️ Назад'), id='back_to_date', on_click=lambda c, b, m: m.back()),
                    Button(Const('Далее ➡'),id = 'next_to_check',on_click = lambda c, b, m: m.next()),
                    Cancel(text=Const('📛 Отменить'))
        ),
        state=ServicesSG.set_time,
        getter=available_times_getter,
        parse_mode=ParseMode.HTML,
    ))
#     Window(
#         Format("<b>Подтвердите запись:</b>"),
#         Group(
#             Row(
#                         Button(Const('◀️ Назад'), id='back_to_time', on_click=lambda c, b, m: m.back()),
#                                 # Button(Const('✅ Подтвердить'), id='confirm', on_click=on_confirm)),
#                   Column(
#                                 Cancel(text=Const('📛 Отменить')))
#         )
#     )
# )
