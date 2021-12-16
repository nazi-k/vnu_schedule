from app.models import Lesson, WeekDay, Subscriber
from app import utils

from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import datetime

from typing import Tuple, Optional


callback_day = CallbackData("day", "date")


def get_keyboard_day(date_selected: datetime.date) -> InlineKeyboardMarkup:
    previous_day = date_selected - datetime.timedelta(days=1)
    following_day = date_selected + datetime.timedelta(days=1)
    buttons = [
        InlineKeyboardButton(text=f"< {utils.get_d_m_y(previous_day)}",
                             callback_data=callback_day.new(date=f"{previous_day.strftime('%Y-%m-%d')}")),

        InlineKeyboardButton(text="Сьогодні", callback_data=callback_day.new(date=f"{utils.today().date()}")),

        InlineKeyboardButton(text=f"{utils.get_d_m_y(following_day)} >",
                             callback_data=callback_day.new(date=f"{following_day.strftime('%Y-%m-%d')}"))
    ]
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)
    return keyboard


def _get_number_emoji(number: int) -> str:
    number_emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    return number_emojis[number]


def build_lesson(lesson: Lesson, subscriber: Subscriber) -> str:
    """Використовувати parse_mode='HTML'"""
    lesson_str = _get_number_emoji(lesson.number)
    if lesson.subject.url and subscriber.show_online_link:
        lesson_str += "<b>" + f'<a href="{lesson.subject.url}">{lesson.subject.name}</a>' + "</b>"
    else:
        lesson_str += "<b>" + lesson.subject.name + "</b>"
    if lesson.subject.teacher_name:
        lesson_str += "\n🎓 " + lesson.subject.teacher_name + " "
    else:
        lesson_str += "\n"
    if lesson.audience:
        lesson_str += lesson.audience
    if lesson.form:
        lesson_str += "\n📍 " + str(lesson.form)
    if subscriber.show_online_link:
        lesson_str += f" <code>{'змінити' if lesson.subject.url else 'встановити'}</code>" \
                      f" /link" + str(lesson.subject.id)
    lesson_str += "\n" + "🕓" + str(lesson.start_time)[:-3] + " - " + str(lesson.end_time)[:-3]
    if not subscriber.subgroup and lesson.subgroup:
        lesson_str += f" <i>({lesson.subgroup} підгрупа)</i>"

    return lesson_str


def build_day(day: WeekDay, subscriber: Subscriber) -> Optional[str]:
    """Використовувати parse_mode='HTML'"""
    return "\n➖➖➖➖➖➖➖➖➖➖\n".join(
        [build_lesson(lesson, subscriber) for lesson in day.lessons])


def get_day_text(day: WeekDay, subscriber: Subscriber, date_selected: datetime.date) -> str:
    """Використовувати parse_mode='HTML'"""
    day_text = build_day(day, subscriber)
    text = "<b>" + utils.get_weekday_name(date_selected) + "</b>" + f" ({date_selected.strftime('%d.%m')})\n\n"
    text += day_text if day_text else "Заняття відсутні"
    return text

