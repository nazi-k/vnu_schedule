from app import utils

from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import datetime

from typing import Union

callback_week = CallbackData("week", "monday_date", "selected_day")
#                                    datetime.date  datetime.date.weekday()


def get_keyboard_week(monday_selected: datetime.date, selected_day: Union[int, str]) -> InlineKeyboardMarkup:
    previous_monday = monday_selected - datetime.timedelta(days=7)
    following_monday = monday_selected + datetime.timedelta(days=7)
    selected_day = int(selected_day)
    buttons1 = [
        InlineKeyboardButton(text=f"{'❄️' if selected_day == 0 else 'Пн'}",
                             callback_data=callback_week.new(monday_date=f"{monday_selected.strftime('%Y-%m-%d')}",
                                                             selected_day=0)),

        InlineKeyboardButton(text=f"{'❄️' if selected_day == 1 else 'Вт'}",
                             callback_data=callback_week.new(monday_date=f"{monday_selected.strftime('%Y-%m-%d')}",
                                                             selected_day=1)),

        InlineKeyboardButton(text=f"{'❄️' if selected_day == 2 else 'Ср'}",
                             callback_data=callback_week.new(monday_date=f"{monday_selected.strftime('%Y-%m-%d')}",
                                                             selected_day=2)),

        InlineKeyboardButton(text=f"{'❄️' if selected_day == 3 else 'Чт'}",
                             callback_data=callback_week.new(monday_date=f"{monday_selected.strftime('%Y-%m-%d')}",
                                                             selected_day=3)),
        InlineKeyboardButton(text=f"{'❄️' if selected_day == 4 else 'Пт'}",
                             callback_data=callback_week.new(monday_date=f"{monday_selected.strftime('%Y-%m-%d')}",
                                                             selected_day=4)),
        InlineKeyboardButton(text=f"{'❄️' if selected_day == 5 else 'Сб'}",
                             callback_data=callback_week.new(monday_date=f"{monday_selected.strftime('%Y-%m-%d')}",
                                                             selected_day=5)),
        InlineKeyboardButton(text=f"{'❄️' if selected_day == 6 else 'Нд'}",
                             callback_data=callback_week.new(monday_date=f"{monday_selected.strftime('%Y-%m-%d')}",
                                                             selected_day=6)),
    ]
    buttons2 = [
        InlineKeyboardButton(text=f"< {utils.get_d_m_y(previous_monday)}",
                             callback_data=callback_week.new(monday_date=f"{previous_monday.strftime('%Y-%m-%d')}",
                                                             selected_day=0)),

        InlineKeyboardButton(text="Сьогодні",
                             callback_data=callback_week.new(monday_date=f"{utils.get_week_monday()}",
                                                             selected_day=utils.today().date().weekday())),

        InlineKeyboardButton(text=f"{utils.get_d_m_y(following_monday)} >",
                             callback_data=callback_week.new(monday_date=f"{following_monday.strftime('%Y-%m-%d')}",
                                                             selected_day=0))
    ]
    keyboard = InlineKeyboardMarkup(row_width=7)
    keyboard.add(*buttons1)
    keyboard.add(*buttons2)
    return keyboard
